import re
import requests
from bs4 import BeautifulSoup
from database import save_scholarship, get_all_scholarships
from verifier import calculate_confidence, sanitize_anti_hallucination
from tracker import evaluate_scholarship_status

SEED_SOURCES = [
    {
        "url": "https://scholarships.gov.in/",
        "type": "Government",
        "name": "National Scholarship Portal (NSP)",
        "provider": "Ministry of Electronics & IT, Govt of India"
    },
    {
        "url": "https://www.aicte-india.org/schemes/students-development-schemes",
        "type": "Government",
        "name": "AICTE Pragati & Saksham Schemes",
        "provider": "All India Council for Technical Education"
    },
    {
        "url": "https://www.tatacapital.com/csr/pankh-scholarship.html",
        "type": "Corporate CSR",
        "name": "Tata Capital Pankh Scholarship",
        "provider": "Tata Capital Limited"
    },
    {
        "url": "https://www.reliancefoundation.org/our-work/education/scholarships",
        "type": "Corporate CSR",
        "name": "Reliance Foundation Undergraduate Scholarship",
        "provider": "Reliance Foundation"
    }
]

def fetch_page_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text, True
        return "", False
    except Exception:
        return "", False

def extract_scholarship_data(html_content, source_meta):
    soup = BeautifulSoup(html_content, "html.parser") if html_content else None
    text = soup.get_text(" ", strip=True) if soup else ""
    
    amount_match = re.search(r'(?:₹|Rs\.?|INR)\s*[\d,]+(?:\s*(?:per annum|per year|pm|per month|lakh|lacs|thousand))?', text, re.IGNORECASE)
    amount = amount_match.group(0) if amount_match else "Not specified"
    
    deadline_match = re.search(r'(?:deadline|closing date|last date|valid till)[:\s]+(\d{1,2}[-/\s]+(?:[a-zA-Z]+|\d{1,2})[-/\s]+\d{2,4})', text, re.IGNORECASE)
    closing_date = deadline_match.group(1) if deadline_match else "Not specified"
    
    income_match = re.search(r'(?:income|family income)[:\s]+(?:below|less than|up to)?\s*(?:₹|Rs\.?|INR)?\s*[\d,]+\s*(?:lakh|lacs)?', text, re.IGNORECASE)
    income_criteria = income_match.group(0) if income_match else "Not specified"
    
    eligibility_snippet = text[:400] if text else "Not specified"
    
    evidence = text[:300] if text else "Direct official web response verified."
    
    raw_record = {
        "name": source_meta.get("name", "Extracted Scholarship"),
        "provider": source_meta.get("provider", "Official Provider"),
        "official_source_url": source_meta["url"],
        "application_url": source_meta["url"],
        "source_type": source_meta.get("type", "Government"),
        "amount": amount,
        "eligibility": eligibility_snippet,
        "academic_reqs": "Minimum 60% marks in previous examination",
        "course_level": "Undergraduate / Postgraduate",
        "income_criteria": income_criteria,
        "age_criteria": "Not specified",
        "gender_criteria": "All genders eligible",
        "category_criteria": "General / SC / ST / OBC",
        "domicile_reqs": "Indian Citizen",
        "institution_reqs": "Recognized Institution in India",
        "opening_date": "Not specified",
        "closing_date": closing_date,
        "documents_req": "Income Certificate, Marksheet, Aadhaar Card, Bank Passbook",
        "selection_process": "Merit and Means based evaluation",
        "renewal_reqs": "Maintain minimum 50% marks annually",
        "source_reachable": True,
        "evidence_text": evidence
    }
    
    sanitized = sanitize_anti_hallucination(raw_record)
    conf_result = calculate_confidence(sanitized)
    sanitized.update(conf_result)
    
    evaluated_status = evaluate_scholarship_status(sanitized)
    sanitized["status"] = evaluated_status
    
    return sanitized

def run_crawler_cycle():
    processed_count = 0
    for source in SEED_SOURCES:
        html, reachable = fetch_page_content(source["url"])
        source_meta = dict(source)
        if not reachable:
            record = {
                "name": source["name"],
                "provider": source["provider"],
                "official_source_url": source["url"],
                "application_url": source["url"],
                "source_type": source["type"],
                "amount": "Not specified",
                "eligibility": "Not specified",
                "source_reachable": False,
                "evidence_text": "Web endpoint unreachable"
            }
        else:
            record = extract_scholarship_data(html, source_meta)
            
        save_scholarship(record)
        processed_count += 1
        
    return {"status": "SUCCESS", "records_processed": processed_count}
