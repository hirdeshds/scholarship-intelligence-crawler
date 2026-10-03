from datetime import datetime

def evaluate_scholarship_status(record):
    current_status = record.get("status", "REVIEW_REQUIRED")
    source_reachable = record.get("source_reachable", True)
    
    if not source_reachable:
        return "NO_LONGER_VERIFIABLE"
        
    closing_date_str = record.get("closing_date", "")
    if closing_date_str and closing_date_str != "Not specified":
        try:
            for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"]:
                try:
                    dt = datetime.strptime(closing_date_str.strip(), fmt)
                    now = datetime.now()
                    if dt < now:
                        return "EXPIRED"
                    days_left = (dt - now).days
                    if days_left <= 15 and days_left >= 0:
                        return "EXPIRING_SOON"
                    break
                except ValueError:
                    continue
        except Exception:
            pass
            
    return current_status

def detect_field_changes(old_record, new_record):
    changes = []
    track_fields = [
        "amount", "eligibility", "closing_date", "income_criteria", 
        "status", "application_url", "official_source_url"
    ]
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for f in track_fields:
        old_val = str(old_record.get(f, "")).strip()
        new_val = str(new_record.get(f, "")).strip()
        
        if old_val and new_val and old_val != new_val and new_val != "Not specified":
            changes.append({
                "field_name": f,
                "old_value": old_val,
                "new_value": new_val,
                "date_detected": now_str,
                "official_source_url": new_record.get("official_source_url", old_record.get("official_source_url", "")),
                "evidence_text": new_record.get("evidence_text", old_record.get("evidence_text", ""))
            })
            
    return changes
