# NoticeGuard

**A verified-source watchdog for government-exam aspirants.** NoticeGuard watches official commission websites (UPSC, SSC, state PSCs), detects new notices, classifies them, checks that they come from an official domain, and sends a plain-language alert.

Built by **Team TheHouse** (Ayush Kaushik, Devin Anand) for **HackIIITD 2026** (IIIT Delhi, Esya '26), powered by the [TinyFish API](https://agent.tinyfish.ai).

## The problem
Notices, corrigenda, date changes and results are scattered across dozens of commission sites, mostly as PDFs with no API. In our live test, only 2 of the first 9 search results for a UPSC notification query came from the official site; the rest were social posts and coaching blogs.

## How it works
```
Official sites -> TinyFish (Agent / Fetch / Search) -> LLM classify + summarize
              -> verify (official domain, link opens) -> SQLite -> web feed + Telegram alerts
```
| Stage | TinyFish API | Code |
|---|---|---|
| Navigate notice boards with no API | Agent | `app/tinyfish_client.py: extract_notices` |
| Read full notice PDFs/pages as markdown | Fetch | `app/tinyfish_client.py: fetch_text` |
| Discover candidate pages, flag official domains | Search | `app/tinyfish_client.py: discover` |
| Detect page changes (planned) | Monitor | not built yet |

Search and Fetch are free; only Agent runs use credits, so the pipeline uses Agent only where navigation is needed.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # add your keys
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000. With `DEMO_MODE=1` (default) it loads `data/sample_notices.json`, real SSC/UPSC notices captured from live TinyFish runs, so the app works without credits or network. Set `DEMO_MODE=0` and a `TINYFISH_API_KEY` to run live; then `POST /api/refresh` (or the button in the UI) runs the Agent on each source.

Run tests: `pytest`

## API
| Endpoint | Description |
|---|---|
| `GET /api/alerts?type=all` | Stored notices, newest first |
| `POST /api/refresh?demo=false&check_links=true` | Run the pipeline, return new notices |
| `GET /api/discover?q=UPSC corrigendum 2026` | TinyFish Search, official domains flagged |
| `GET /api/health` | Status |

## Add a new commission
Add one dict to `app/sources.py` (id, name, url, goal). Nothing else changes.

## Known limits
- Read-only, public pages only. No logins, captcha or form filling.
- The Agent can return coarse notice types, so classification is done in our LLM layer (`app/classify.py`, keyword fallback without an API key).
- Domain verification must run on the URL we requested, not the final URL Fetch resolves to (it can be a raw IP).
- Not yet built: Monitor-based change detection, WhatsApp alerts, user accounts and per-user exam selection.

## Design
`docs/` has the three prototype screens (Figma Make) and the Round 1 deck.

## License
MIT
