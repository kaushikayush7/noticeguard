from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
from app.sources import SOURCES

router = APIRouter()

def init_dashboard_db():
    conn = sqlite3.connect("noticeguard.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS aspirants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gmail TEXT,
            telegram_chat_id TEXT UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS aspirant_exams (
            aspirant_id INTEGER,
            exam_id TEXT,
            FOREIGN KEY(aspirant_id) REFERENCES aspirants(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS telegram_subscribers (
            chat_id TEXT PRIMARY KEY,
            subscribed_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

@router.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request, chat_id: str = None):
    init_dashboard_db()
    conn = sqlite3.connect("noticeguard.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Show Aspirant Login Page if no chat_id provided
    if not chat_id:
        conn.close()
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NoticeGuard | Aspirant Login</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gradient-to-br from-indigo-900 via-blue-900 to-slate-900 min-h-screen flex items-center justify-center p-6">
            <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 border border-gray-100">
                <div class="text-center mb-8">
                    <span class="text-4xl">🛡️</span>
                    <h1 class="text-2xl font-extrabold text-gray-900 mt-2">NoticeGuard Portal</h1>
                    <p class="text-sm text-gray-500 mt-1">Real-time AI Exam Intelligence & Alert System</p>
                </div>
                <form action="/login" method="POST" class="space-y-5">
                    <div>
                        <label class="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-1">Full Name</label>
                        <input type="text" name="name" required placeholder="e.g. Ayush Kaushik" class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-600 focus:outline-none text-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-1">Gmail Address</label>
                        <input type="email" name="gmail" required placeholder="aspirant@gmail.com" class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-600 focus:outline-none text-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-1">Telegram Chat ID</label>
                        <input type="text" name="chat_id" required placeholder="e.g. 8608954908" class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-600 focus:outline-none text-sm">
                        <p class="text-xs text-gray-400 mt-1">Get your ID from @userinfobot on Telegram</p>
                    </div>
                    <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-xl font-semibold hover:bg-indigo-700 transition shadow-lg shadow-indigo-600/30">Continue to Exam Selection</button>
                </form>
            </div>
        </body>
        </html>
        """)

    aspirant = c.execute("SELECT * FROM aspirants WHERE telegram_chat_id = ?", (chat_id,)).fetchone()
    if not aspirant:
        conn.close()
        return RedirectResponse(url="/", status_code=303)

    selected_exams = [row['exam_id'] for row in c.execute("SELECT exam_id FROM aspirant_exams WHERE aspirant_id = ?", (aspirant['id'],)).fetchall()]

    # 2. Show Exam Selection Page if no exams picked yet
    if not selected_exams:
        sources_html = ""
        for src in SOURCES:
            sources_html += f"""
            <label class="flex items-center space-x-3 p-3 rounded-xl border border-gray-200 hover:bg-indigo-50/50 cursor-pointer transition">
                <input type="checkbox" name="exams" value="{src['id']}" class="w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500">
                <div>
                    <p class="text-sm font-semibold text-gray-800">{src['name']}</p>
                    <p class="text-xs text-gray-500">Target official portal notices</p>
                </div>
            </label>
            """
        conn.close()
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Select Exams | NoticeGuard</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50 min-h-screen py-10 px-4">
            <div class="max-w-2xl mx-auto bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                <div class="mb-6">
                    <h1 class="text-2xl font-bold text-gray-900">Welcome, {aspirant['name']}! 👋</h1>
                    <p class="text-sm text-gray-500 mt-1">Select the exams you want to track. You will receive instant Telegram & Email alerts for these exams.</p>
                </div>
                <form action="/save-exams?chat_id={chat_id}" method="POST" class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto p-1">
                        {sources_html}
                    </div>
                    <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-xl font-semibold hover:bg-indigo-700 transition shadow-lg shadow-indigo-600/30 mt-6">Save Preferences & View Dashboard</button>
                </form>
            </div>
        </body>
        </html>
        """)

    # 3. Show Personalized Dashboard (matching your requested UI style)
    placeholders = ','.join(['?'] * len(selected_exams))
    notices = c.execute(f"SELECT * FROM notices WHERE exam_id IN ({placeholders}) ORDER BY id DESC LIMIT 30", selected_exams).fetchall()
    
    notices_html = ""
    for n in notices:
        notices_html += f"""
        <tr class="border-b hover:bg-gray-50 transition-colors">
            <td class="px-4 md:px-6 py-4 text-xs md:text-sm font-semibold text-indigo-600 whitespace-nowrap">{n['exam_id']}</td>
            <td class="px-4 md:px-6 py-4 text-xs md:text-sm font-medium text-gray-900">{n['title']}</td>
            <td class="px-4 md:px-6 py-4 text-xs md:text-sm text-gray-600 whitespace-nowrap"><span class="bg-blue-100 text-blue-800 text-xs px-2.5 py-1 rounded-full">{n['notice_type']}</span></td>
            <td class="px-4 md:px-6 py-4 text-xs md:text-sm text-gray-500 whitespace-nowrap">{n['published_date']}</td>
            <td class="px-4 md:px-6 py-4 text-xs md:text-sm whitespace-nowrap"><a href="{n['source_url']}" target="_blank" class="text-indigo-600 hover:text-indigo-900 font-medium underline">View Source</a></td>
        </tr>
        """

    conn.close()
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NoticeGuard | HackIIITD 2026 Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 min-h-screen">
        <nav class="bg-gradient-to-r from-indigo-700 to-blue-600 text-white shadow-md">
            <div class="max-w-7xl mx-auto px-4 md:px-6 py-4 flex flex-col sm:flex-row justify-between items-center gap-3">
                <div class="flex items-center space-x-3">
                    <span class="text-2xl md:text-3xl">🛡️</span>
                    <div>
                        <h1 class="text-xl md:text-2xl font-bold">NoticeGuard</h1>
                        <p class="text-xs text-indigo-200">Automated Exam Intelligence & Change Detection ({aspirant['name']})</p>
                    </div>
                </div>
                <div class="flex items-center space-x-3">
                    <span class="bg-indigo-500/50 border border-indigo-400 px-3 py-1 rounded-full text-xs md:text-sm font-medium">HackIIITD 2026</span>
                    <a href="/" class="bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg text-xs md:text-sm transition">Switch User</a>
                </div>
            </div>
        </nav>
        
        <main class="max-w-7xl mx-auto px-4 md:px-6 py-6 md:py-8">
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
                <div class="bg-white p-5 md:p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 class="text-gray-500 text-xs font-semibold uppercase tracking-wider">Total Notices Tracked</h3>
                    <p class="text-2xl md:text-3xl font-extrabold text-indigo-600 mt-2">{len(notices)}</p>
                </div>
                <div class="bg-white p-5 md:p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 class="text-gray-500 text-xs font-semibold uppercase tracking-wider">Monitored Portals</h3>
                    <p class="text-2xl md:text-3xl font-extrabold text-emerald-600 mt-2">12 Active</p>
                </div>
                <div class="bg-white p-5 md:p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 class="text-gray-500 text-xs font-semibold uppercase tracking-wider">Alert Channels</h3>
                    <p class="text-2xl md:text-3xl font-extrabold text-blue-600 mt-2">Telegram & SMTP</p>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div class="px-4 md:px-6 py-4 md:py-5 border-b border-gray-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 bg-gray-50/50">
                    <div>
                        <h2 class="text-base md:text-lg font-bold text-gray-800">Live Exam Notifications & Page Changes</h2>
                        <p class="text-xs text-gray-500 mt-0.5">Real-time sync from SQLite database</p>
                    </div>
                    <button onclick="location.reload()" class="w-full sm:w-auto bg-indigo-600 text-white px-4 py-2 rounded-lg text-xs md:text-sm font-medium hover:bg-indigo-700 transition shadow-sm">Refresh Data</button>
                </div>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-4 md:px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">Exam ID</th>
                                <th class="px-4 md:px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Notice Title</th>
                                <th class="px-4 md:px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">Type</th>
                                <th class="px-4 md:px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">Date</th>
                                <th class="px-4 md:px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">Source Link</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            {notices_html if notices_html else '<tr><td colspan="5" class="px-6 py-8 text-center text-gray-500 text-sm">No notices found for your selected exams. Run <code class="bg-gray-100 px-2 py-1 rounded text-indigo-600 font-mono">python -m app.monitor</code> to sync data.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </body>
    </html>
    """)

@router.post("/login")
def login_aspirant(name: str = Form(...), gmail: str = Form(...), chat_id: str = Form(...)):
    init_dashboard_db()
    conn = sqlite3.connect("noticeguard.db")
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO aspirants (name, gmail, telegram_chat_id)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_chat_id) DO UPDATE SET name = ?, gmail = ?
        ''', (name, gmail, chat_id, name, gmail))
        
        c.execute('''
            INSERT INTO telegram_subscribers (chat_id, subscribed_at)
            VALUES (?, datetime('now'))
            ON CONFLICT(chat_id) DO NOTHING
        ''', (chat_id,))
        
        conn.commit()
    except Exception as e:
        print(f"Login error: {e}")
    conn.close()
    return RedirectResponse(url=f"/?chat_id={chat_id}", status_code=303)

@router.post("/save-exams")
def save_exams(chat_id: str, exams: list[str] = Form(...)):
    conn = sqlite3.connect("noticeguard.db")
    c = conn.cursor()
    aspirant = c.execute("SELECT id FROM aspirants WHERE telegram_chat_id = ?", (chat_id,)).fetchone()
    if aspirant:
        aspirant_id = aspirant[0]
        c.execute("DELETE FROM aspirant_exams WHERE aspirant_id = ?", (aspirant_id,))
        for exam_id in exams:
            c.execute("INSERT INTO aspirant_exams (aspirant_id, exam_id) VALUES (?, ?)", (aspirant_id, exam_id))
        conn.commit()
    conn.close()
    return RedirectResponse(url=f"/?chat_id={chat_id}", status_code=303)
