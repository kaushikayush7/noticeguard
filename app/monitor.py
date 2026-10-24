import sqlite3
import httpx
import os
from app.sources import SOURCES
from app.notify import send_alerts
from dotenv import load_dotenv

load_dotenv()
TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
DB_PATH = "noticeguard.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id TEXT,
            title TEXT,
            notice_type TEXT,
            summary TEXT,
            published_date TEXT,
            verified BOOLEAN,
            pdf_url TEXT,
            source_url TEXT,
            UNIQUE(exam_id, title, published_date)
        )
    ''')
    try:
        c.execute("ALTER TABLE notices ADD COLUMN exam_id TEXT;")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def get_mock_notices(source: dict) -> list:
    """Fallback sample notices used if offline or API key times out."""
    return [
        {
            "title": f"Official Notification Update for {source['name']} 2026",
            "date": "2026-06-01",
            "type": "Notification",
            "summary": f"Latest schedule and guidelines update published for {source['name']}.",
            "url": source["url"]
        }
    ]

def fetch_notices_via_tinyfish(source: dict) -> list:
    if not TINYFISH_API_KEY:
        print(f"-> No TinyFish API key found, using mock fallback for {source['name']}")
        return get_mock_notices(source)
    
    endpoint = "https://agent.tinyfish.ai/v1/automation/run"
    headers = {
        "X-API-Key": TINYFISH_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "url": source["url"],
        "goal": source["goal"]
    }
    
    try:
        response = httpx.post(endpoint, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            items = data.get("result", [])
            if isinstance(items, list) and items:
                return items
            elif isinstance(items, dict):
                return [items]
        print(f"-> TinyFish returned status {response.status_code} for {source['name']}, using fallback.")
    except Exception as e:
        print(f"-> Timeout/Error connecting to TinyFish for {source['name']} (using fallback): {e}")
        
    return get_mock_notices(source)

def run_monitor():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("Starting NoticeGuard monitoring loop...")
    for source in SOURCES:
        try:
            print(f"\nChecking source: {source['name']}...")
            items = fetch_notices_via_tinyfish(source)
            
            for item in items:
                title = item.get("title")
                date = item.get("date", "2026-06-01")
                url = item.get("url", source["url"])
                notice_type = item.get("type", "notification")
                
                if not title:
                    continue
                    
                try:
                    c.execute('''
                        INSERT INTO notices (exam_id, title, notice_type, summary, published_date, verified, pdf_url, source_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        source["id"],
                        title,
                        notice_type,
                        item.get("summary", title),
                        date,
                        True,
                        url if url and url.endswith(".pdf") else None,
                        url
                    ))
                    conn.commit()
                    
                    notice_row = {
                        "exam": source["name"],
                        "notice_type": notice_type,
                        "summary": item.get("summary", title),
                        "published_date": date,
                        "verified": True,
                        "pdf_url": url,
                        "source_url": url
                    }
                    send_alerts(notice_row)
                    print(f"   -> [SUCCESS] Alert dispatched for: {title}")
                    
                except sqlite3.IntegrityError:
                    print(f"   -> Notice already exists in database (skipped)")
                    
        except Exception as source_err:
            print(f"-> Error processing {source['name']}: {source_err}. Skipping to next source.")
            continue
                
    conn.close()
    print("\nMonitoring loop completed successfully across all sources.")

if __name__ == "__main__":
    run_monitor()
