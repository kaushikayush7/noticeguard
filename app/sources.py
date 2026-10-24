"""One entry per commission. Adding a new source = adding one dict here."""

SOURCES = [
    {
        "id": "ssc",
        "name": "Staff Selection Commission",
        "url": "https://ssc.gov.in",
        "goal": (
            "Go to the Notice Board on this website and click 'View all'. From the list page only, "
            "return the 5 most recent notices with: title, published_date, exam_name (or null) and "
            "pdf_url (full https link if visible, else null). Do not open any PDFs. "
            "Only use information visible on this website."
        ),
    },
    {
        "id": "upsc",
        "name": "Union Public Service Commission",
        "url": "https://upsc.gov.in",
        "goal": (
            "Find the latest examination notices or announcements on this website. Return the 5 most recent "
            "with: title, published_date, exam_name (or null) and pdf_url (full https link if visible, else null). "
            "Do not open any PDFs. Only use information visible on this website."
        ),
    },
]


