"""Applies the exam-selection fix to app/routers/dashboard.py.

Run from the project root (C:\\noticeguard):   python apply_exam_fix.py
- Makes a backup first: app/routers/dashboard.py.bak
- Changes nothing if any expected line is not found.
"""
import shutil
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "app/routers/dashboard.py"

EDITS = [
    # 1. accept ?edit=1 so the checklist can be reopened
    ("def get_dashboard(request: Request, chat_id: str = None):",
     "def get_dashboard(request: Request, chat_id: str = None, edit: bool = False):"),
    # 2. show the checklist when nothing is saved OR when editing
    ("    if not selected_exams:\n",
     "    if not selected_exams or edit:\n"),
    # 3. pre-tick the exams that are already saved
    ("value=\"{src['id']}\" class=\"w-4 h-4",
     "value=\"{src['id']}\" {'checked' if src['id'] in selected_exams else ''} class=\"w-4 h-4"),
    # 4. Edit Exams button on the dashboard
    ("<a href=\"/\" class=\"bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg text-xs md:text-sm transition\">Switch User</a>",
     "<a href=\"/?chat_id={chat_id}&edit=1\" class=\"bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg text-xs md:text-sm transition\">Edit Exams</a>\n"
     "                    <a href=\"/\" class=\"bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg text-xs md:text-sm transition\">Switch User</a>"),
    # 5. saving with nothing ticked goes back to the checklist instead of a 422 error
    ("def save_exams(chat_id: str, exams: list[str] = Form(...)):\n",
     "def save_exams(chat_id: str, exams: list[str] = Form(default=[])):\n"
     "    if not exams:\n"
     "        return RedirectResponse(url=f\"/?chat_id={chat_id}&edit=1\", status_code=303)\n"),
]

with open(PATH, encoding="utf-8-sig") as f:
    text = f.read()

if "edit: bool = False" in text:
    sys.exit("Already patched. Nothing to do.")

for i, (old, new) in enumerate(EDITS, 1):
    n = text.count(old)
    if n != 1:
        sys.exit(f"Edit {i} not applied: expected 1 match, found {n}. No changes were made.")
    text = text.replace(old, new)

shutil.copyfile(PATH, PATH + ".bak")
with open(PATH, "w", encoding="utf-8") as f:
    f.write(text)
print(f"Patched {PATH} (backup: {PATH}.bak). Restart is automatic if uvicorn --reload is running.")