from app import classify, db, verify


def test_official_domains():
    assert verify.is_official("https://www.upsc.gov.in/sites/default/files/x.pdf")
    assert verify.is_official("https://upsconline.nic.in")
    assert not verify.is_official("https://www.instagram.com/p/abc")
    assert not verify.is_official("https://gov.in.evil.com/x")
    assert not verify.is_official("https://23.62.46.198/x.pdf")
    assert not verify.is_official(None)


def test_rule_classifier():
    c = classify.classify_rules
    assert c("Uploading Tentative Answer Keys and inviting challenges")["notice_type"] == "answer_key"
    assert c("Shortlisting of candidates for PET")["notice_type"] == "shortlisting"
    assert c("Tentative Vacancies of Junior Engineer Examination")["notice_type"] == "vacancy"
    assert c("Declaration of Final Result")["notice_type"] == "result"
    assert c("Civil Services Examination, 2026: Examination Notice No. 05/2026-CSE")["notice_type"] == "new_notification"
    assert c("Something unrelated")["notice_type"] == "other"


def test_dates_and_ids():
    assert db.normalize_date("12 Oct 2026") == "2026-10-12"
    assert db.notice_id("ssc", "a", "2026-10-12") == db.notice_id("ssc", "a", "2026-10-12")
