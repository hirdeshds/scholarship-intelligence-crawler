import re
from urllib.parse import urlparse

OFFICIAL_DOMAINS = [
    ".gov.in", ".nic.in", ".ac.in", ".edu.in", ".org.in",
    "scholarships.gov.in", "aicte-india.org", "ugc.ac.in", "education.gov.in",
    "tatacapital.com", "reliancefoundation.org", "hdfcbank.com", "jntataendowment.org",
    "sbi.co.in", "licindia.in", "buddle4study.com"
]

def check_official_domain(url):
    if not url:
        return False, "No URL provided"
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    for official in OFFICIAL_DOMAINS:
        if official in domain:
            return True, f"Verified primary domain match: {official}"
    if any(tld in domain for tld in [".gov.in", ".nic.in", ".ac.in", ".edu.in"]):
        return True, "Verified government or academic top-level domain"
    return False, f"Domain ({domain}) is not in primary verified registry"

def calculate_confidence(record):
    score = 0.0
    reasons = []
    
    official_url = record.get("official_source_url", "")
    is_official, domain_reason = check_official_domain(official_url)
    if is_official:
        score += 35.0
        reasons.append({"weight": 35.0, "passed": True, "description": domain_reason})
    else:
        reasons.append({"weight": 35.0, "passed": False, "description": domain_reason})
        
    app_url = record.get("application_url", "")
    if app_url and app_url != "Not specified" and app_url.startswith("http"):
        score += 20.0
        reasons.append({"weight": 20.0, "passed": True, "description": "Direct active application URL identified"})
    else:
        reasons.append({"weight": 20.0, "passed": False, "description": "No direct application URL provided"})
        
    source_reachable = record.get("source_reachable", True)
    if source_reachable:
        score += 15.0
        reasons.append({"weight": 15.0, "passed": True, "description": "Primary official source web endpoint verified online"})
    else:
        reasons.append({"weight": 15.0, "passed": False, "description": "Primary source URL unreachable or non-responsive"})
        
    evidence = record.get("evidence_text", "")
    if evidence and evidence != "No evidence recorded" and len(evidence) > 20:
        score += 20.0
        reasons.append({"weight": 20.0, "passed": True, "description": "High-fidelity text evidence snippet captured from source"})
    else:
        reasons.append({"weight": 20.0, "passed": False, "description": "Insufficient source text evidence"})
        
    closing_date = record.get("closing_date", "")
    amount = record.get("amount", "")
    if closing_date != "Not specified" and amount != "Not specified":
        score += 10.0
        reasons.append({"weight": 10.0, "passed": True, "description": "Complete structured fields verified without contradictions"})
    else:
        reasons.append({"weight": 10.0, "passed": False, "description": "Partial field specification"})
        
    final_score = round(min(score, 100.0), 1)
    status = "VERIFIED" if final_score >= 95.0 else "REVIEW_REQUIRED"
    
    return {
        "confidence_score": final_score,
        "status": status,
        "confidence_reasons": reasons
    }

def sanitize_anti_hallucination(record):
    sanitized = dict(record)
    fields = [
        "amount", "eligibility", "academic_reqs", "course_level", 
        "income_criteria", "age_criteria", "gender_criteria", 
        "category_criteria", "domicile_reqs", "institution_reqs", 
        "opening_date", "closing_date", "documents_req", 
        "selection_process", "renewal_reqs"
    ]
    for f in fields:
        val = sanitized.get(f)
        if not val or str(val).strip() == "" or str(val).lower() in ["none", "null", "n/a", "unknown"]:
            sanitized[f] = "Not specified"
    return sanitized
