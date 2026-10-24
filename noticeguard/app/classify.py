"""LLM layer: classify a notice and write a one-line summary. Falls back to keywords with no API key."""
import json
import os

from .config import ANTHROPIC_MODEL

TYPES = ["new_notification", "corrigendum", "date_change", "answer_key", "shortlisting",
         "vacancy", "result", "admit_card", "other"]

_RULES = [  # order matters: most specific first
    ("answer key", "answer_key"), ("response sheet", "answer_key"),
    ("shortlist", "shortlisting"), ("vacanc", "vacancy"),
    ("admit card", "admit_card"), ("e-admit", "admit_card"),
    ("corrigendum", "corrigendum"), ("addendum", "corrigendum"),
    ("extended", "date_change"), ("rescheduled", "date_change"), ("postponed", "date_change"),
    ("result", "result"), ("marks", "result"),
    ("examination notice", "new_notification"), ("notification", "new_notification"),
]


def classify_rules(title: str) -> dict:
    t = title.lower()
    kind = next((k for needle, k in _RULES if needle in t), "other")
    return {"notice_type": kind, "summary": title.strip().rstrip(".")}


def classify(title: str, text: str = "") -> dict:
    if not os.getenv("ANTHROPIC_API_KEY"):
        return classify_rules(title)
    try:
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=300,
            system=("You classify Indian government-exam notices. Reply with JSON only: "
                    '{"notice_type": one of %s, "summary": one plain-English sentence under 25 words}.' % TYPES),
            messages=[{"role": "user", "content": f"Title: {title}\n\nText:\n{text[:4000]}"}],
        )
        data = json.loads(msg.content[0].text)
        if data.get("notice_type") not in TYPES:
            data["notice_type"] = "other"
        return {"notice_type": data["notice_type"], "summary": data.get("summary") or title}
    except Exception:
        return classify_rules(title)
