from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import sqlite3

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def get_dashboard():
    conn = sqlite3.connect("noticeguard.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        notices = c.execute("SELECT * FROM notices ORDER BY id DESC LIMIT 30").fetchall()
    except sqlite3.OperationalError:
        notices = []
    conn.close()

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

    html = f"""
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
                        <p class="text-xs text-indigo-200">Automated Exam Intelligence & Change Detection</p>
                    </div>
                </div>
                <div>
                    <span class="bg-indigo-500/50 border border-indigo-400 px-3 py-1 rounded-full text-xs md:text-sm font-medium">HackIIITD 2026</span>
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
                            {notices_html if notices_html else '<tr><td colspan="5" class="px-6 py-8 text-center text-gray-500 text-sm">No notices recorded yet. Run <code class="bg-gray-100 px-2 py-1 rounded text-indigo-600 font-mono">python -m app.monitor</code> to populate data.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
