"""Extra exam sources. Merged into SOURCES by app/sources.py (see step 2)."""
from urllib.parse import urlparse

# Natural-language instruction for the TinyFish Agent. Same for every source.
GOAL = (
    "Open this official page and find the notice / announcement / news section. "
    "Return the 10 most recent items as JSON with fields: title, date, url, type "
    "(notification, admit card, result, corrigendum, date change, other). "
    "Read only. Do not log in or fill forms."
)


def _src(id, name, url, region, category, tags):
    return {
        "id": id,
        "name": name,
        "url": url,
        "goal": GOAL,
        "region": region,        # extra keys: harmless if unused
        "category": category,
        "tags": tags,            # used to match user subscriptions
    }


EXTRA_SOURCES = [
    # ---------- India: central recruitment & civil services ----------
    _src("upsc", "UPSC Civil Services", "https://upsc.gov.in", "IN", "civil_services", ["UPSC", "IAS", "IPS"]),
    _src("ssc", "Staff Selection Commission (SSC)", "https://ssc.gov.in", "IN", "staff_selection", ["SSC", "CGL", "CHSL"]),

    # ---------- India: national entrance exams (NTA and others) ----------
    _src("jee_main", "JEE Main (NTA)", "https://jeemain.nta.nic.in", "IN", "engineering", ["JEE", "JEE MAIN"]),
    _src("jee_adv", "JEE Advanced", "https://jeeadv.ac.in", "IN", "engineering", ["JEE", "JEE ADVANCED"]),
    _src("neet_ug", "NEET UG (NTA)", "https://neet.nta.nic.in", "IN", "medical", ["NEET"]),
    _src("cuet_ug", "CUET UG (NTA)", "https://cuet.nta.nic.in", "IN", "university", ["CUET"]),
    _src("ugc_net", "UGC NET (NTA)", "https://ugcnet.nta.nic.in", "IN", "research", ["UGC NET", "NET"]),
    _src("nta_main", "NTA Official", "https://nta.ac.in", "IN", "general", ["NTA"]),
    _src("cat", "CAT (IIMs)", "https://iimcat.ac.in", "IN", "management", ["CAT", "MBA"]),
    _src("xat", "XAT", "https://xatonline.in", "IN", "management", ["XAT", "MBA"]),
    _src("clat", "CLAT (Consortium of NLUs)", "https://consortiumofnlus.ac.in", "IN", "law", ["CLAT", "LAW"]),
    _src("nift", "NIFT Entrance", "https://nift.ac.in", "IN", "design", ["NIFT"]),

    # ---------- India: banking, railway, defence ----------
    _src("ibps", "IBPS (Banking)", "https://www.ibps.in", "IN", "banking", ["IBPS", "BANK"]),
    _src("sbi", "SBI Careers", "https://sbi.co.in/web/careers", "IN", "banking", ["SBI", "BANK"]),
    _src("rrb", "Railway Recruitment Boards", "https://www.rrbcdg.gov.in", "IN", "railway", ["RRB", "RAILWAY"]),
    _src("army", "Join Indian Army", "https://joinindianarmy.nic.in", "IN", "defence", ["ARMY", "AGNIVEER"]),

    # ---------- India: state public service commissions ----------
    _src("uppsc", "UPPSC", "https://uppsc.up.nic.in", "IN", "state_psc", ["UPPSC", "UP PSC"]),
    _src("bpsc", "BPSC", "https://www.bpsc.bihar.gov.in", "IN", "state_psc", ["BPSC", "BIHAR PSC"]),
    _src("mpsc", "MPSC (Maharashtra)", "https://mpsc.gov.in", "IN", "state_psc", ["MPSC"]),
    _src("rpsc", "RPSC (Rajasthan)", "https://rpsc.rajasthan.gov.in", "IN", "state_psc", ["RPSC"]),
    _src("tnpsc", "TNPSC (Tamil Nadu)", "https://www.tnpsc.gov.in", "IN", "state_psc", ["TNPSC"]),
    _src("kpsc", "KPSC (Karnataka)", "https://kpsc.kar.nic.in", "IN", "state_psc", ["KPSC"]),
    _src("hpsc", "HPSC (Haryana)", "https://hpsc.gov.in", "IN", "state_psc", ["HPSC"]),

    # ---------- Global: study abroad and admissions tests ----------
    _src("sat", "SAT (College Board)", "https://satsuite.collegeboard.org/sat", "US", "undergrad", ["SAT"]),
    _src("ap", "AP Exams (College Board)", "https://apstudents.collegeboard.org", "US", "undergrad", ["AP"]),
    _src("act", "ACT", "https://www.act.org", "US", "undergrad", ["ACT"]),
    _src("gre", "GRE (ETS)", "https://www.ets.org/gre.html", "US", "grad", ["GRE"]),
    _src("toefl", "TOEFL (ETS)", "https://www.ets.org/toefl.html", "US", "language", ["TOEFL"]),
    _src("gmat", "GMAT", "https://www.mba.com/exams/gmat-exam", "US", "management", ["GMAT", "MBA"]),
    _src("ielts", "IELTS", "https://ielts.org", "UK", "language", ["IELTS"]),
    _src("pte", "PTE Academic", "https://www.pearsonpte.com", "UK", "language", ["PTE"]),
    _src("lsat", "LSAT (LSAC)", "https://www.lsac.org/lsat", "US", "law", ["LSAT", "LAW"]),
    _src("mcat", "MCAT (AAMC)", "https://students-residents.aamc.org/mcat", "US", "medical", ["MCAT"]),
    _src("ucat", "UCAT", "https://www.ucat.ac.uk", "UK", "medical", ["UCAT"]),
]


def official_domains() -> set[str]:
    """Host names of all extra sources, for the official-domain verification step."""
    hosts = set()
    for s in EXTRA_SOURCES:
        h = urlparse(s["url"]).netloc.lower()
        hosts.add(h[4:] if h.startswith("www.") else h)
    return hosts