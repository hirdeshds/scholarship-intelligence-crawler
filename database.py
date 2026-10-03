import sqlite3
import json
from datetime import datetime

DB_FILE = "scholarships.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scholarships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        provider TEXT NOT NULL,
        official_source_url TEXT NOT NULL,
        application_url TEXT,
        source_type TEXT NOT NULL,
        amount TEXT NOT NULL,
        eligibility TEXT NOT NULL,
        academic_reqs TEXT,
        course_level TEXT,
        income_criteria TEXT,
        age_criteria TEXT,
        gender_criteria TEXT,
        category_criteria TEXT,
        domicile_reqs TEXT,
        institution_reqs TEXT,
        opening_date TEXT,
        closing_date TEXT,
        documents_req TEXT,
        selection_process TEXT,
        renewal_reqs TEXT,
        status TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        confidence_reasons TEXT,
        last_verified TEXT NOT NULL,
        evidence_text TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS change_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scholarship_id INTEGER NOT NULL,
        field_name TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT,
        date_detected TEXT NOT NULL,
        official_source_url TEXT,
        evidence_text TEXT,
        FOREIGN KEY (scholarship_id) REFERENCES scholarships (id)
    )
    """)
    
    conn.commit()
    conn.close()

def save_scholarship(data):
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reasons_str = json.dumps(data.get("confidence_reasons", []))
    
    cursor.execute("SELECT * FROM scholarships WHERE name = ?", (data["name"],))
    existing = cursor.fetchone()
    
    if existing:
        scholarship_id = existing["id"]
        changes = []
        
        track_fields = [
            "amount", "eligibility", "closing_date", "status", 
            "income_criteria", "application_url", "official_source_url"
        ]
        
        for field in track_fields:
            old_val = str(existing[field]) if existing[field] is not None else ""
            new_val = str(data.get(field, "")) if data.get(field) is not None else ""
            
            if old_val != new_val and new_val != "":
                changes.append((
                    scholarship_id,
                    field,
                    old_val,
                    new_val,
                    now,
                    data.get("official_source_url", existing["official_source_url"]),
                    data.get("evidence_text", existing["evidence_text"])
                ))
        
        cursor.execute("""
        UPDATE scholarships SET
            provider = ?,
            official_source_url = ?,
            application_url = ?,
            source_type = ?,
            amount = ?,
            eligibility = ?,
            academic_reqs = ?,
            course_level = ?,
            income_criteria = ?,
            age_criteria = ?,
            gender_criteria = ?,
            category_criteria = ?,
            domicile_reqs = ?,
            institution_reqs = ?,
            opening_date = ?,
            closing_date = ?,
            documents_req = ?,
            selection_process = ?,
            renewal_reqs = ?,
            status = ?,
            confidence_score = ?,
            confidence_reasons = ?,
            last_verified = ?,
            evidence_text = ?,
            updated_at = ?
        WHERE id = ?
        """, (
            data.get("provider", existing["provider"]),
            data.get("official_source_url", existing["official_source_url"]),
            data.get("application_url", existing["application_url"]),
            data.get("source_type", existing["source_type"]),
            data.get("amount", existing["amount"]),
            data.get("eligibility", existing["eligibility"]),
            data.get("academic_reqs", existing["academic_reqs"]),
            data.get("course_level", existing["course_level"]),
            data.get("income_criteria", existing["income_criteria"]),
            data.get("age_criteria", existing["age_criteria"]),
            data.get("gender_criteria", existing["gender_criteria"]),
            data.get("category_criteria", existing["category_criteria"]),
            data.get("domicile_reqs", existing["domicile_reqs"]),
            data.get("institution_reqs", existing["institution_reqs"]),
            data.get("opening_date", existing["opening_date"]),
            data.get("closing_date", existing["closing_date"]),
            data.get("documents_req", existing["documents_req"]),
            data.get("selection_process", existing["selection_process"]),
            data.get("renewal_reqs", existing["renewal_reqs"]),
            data.get("status", existing["status"]),
            data.get("confidence_score", existing["confidence_score"]),
            reasons_str,
            now,
            data.get("evidence_text", existing["evidence_text"]),
            now,
            scholarship_id
        ))
        
        for change in changes:
            cursor.execute("""
            INSERT INTO change_logs (scholarship_id, field_name, old_value, new_value, date_detected, official_source_url, evidence_text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, change)
            
    else:
        cursor.execute("""
        INSERT INTO scholarships (
            name, provider, official_source_url, application_url, source_type,
            amount, eligibility, academic_reqs, course_level, income_criteria,
            age_criteria, gender_criteria, category_criteria, domicile_reqs,
            institution_reqs, opening_date, closing_date, documents_req,
            selection_process, renewal_reqs, status, confidence_score,
            confidence_reasons, last_verified, evidence_text, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"],
            data.get("provider", "Not specified"),
            data.get("official_source_url", ""),
            data.get("application_url", "Not specified"),
            data.get("source_type", "Government"),
            data.get("amount", "Not specified"),
            data.get("eligibility", "Not specified"),
            data.get("academic_reqs", "Not specified"),
            data.get("course_level", "Not specified"),
            data.get("income_criteria", "Not specified"),
            data.get("age_criteria", "Not specified"),
            data.get("gender_criteria", "Not specified"),
            data.get("category_criteria", "Not specified"),
            data.get("domicile_reqs", "Not specified"),
            data.get("institution_reqs", "Not specified"),
            data.get("opening_date", "Not specified"),
            data.get("closing_date", "Not specified"),
            data.get("documents_req", "Not specified"),
            data.get("selection_process", "Not specified"),
            data.get("renewal_reqs", "Not specified"),
            data.get("status", "REVIEW_REQUIRED"),
            data.get("confidence_score", 0.0),
            reasons_str,
            now,
            data.get("evidence_text", "No evidence recorded"),
            now,
            now
        ))
        scholarship_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return scholarship_id

def get_all_scholarships(query=None, status=None, source_type=None, min_score=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM scholarships WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (name LIKE ? OR provider LIKE ? OR eligibility LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
    if status and status != "ALL":
        sql += " AND status = ?"
        params.append(status)
        
    if source_type and source_type != "ALL":
        sql += " AND source_type = ?"
        params.append(source_type)
        
    if min_score:
        sql += " AND confidence_score >= ?"
        params.append(float(min_score))
        
    sql += " ORDER BY confidence_score DESC, updated_at DESC"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    
    result = []
    for r in rows:
        d = dict(r)
        d["confidence_reasons"] = json.loads(d["confidence_reasons"]) if d["confidence_reasons"] else []
        result.append(d)
        
    conn.close()
    return result

def get_scholarship_by_id(scholarship_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM scholarships WHERE id = ?", (scholarship_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
        
    data = dict(row)
    data["confidence_reasons"] = json.loads(data["confidence_reasons"]) if data["confidence_reasons"] else []
    
    cursor.execute("SELECT * FROM change_logs WHERE scholarship_id = ? ORDER BY date_detected DESC", (scholarship_id,))
    changes = [dict(c) for c in cursor.fetchall()]
    data["change_history"] = changes
    
    conn.close()
    return data

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM scholarships")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM scholarships WHERE confidence_score >= 95.0")
    verified = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM scholarships WHERE confidence_score < 95.0")
    review_required = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM scholarships WHERE status = 'ACTIVE' OR status = 'VERIFIED'")
    active = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM scholarships WHERE status = 'EXPIRED'")
    expired = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT scholarship_id) FROM change_logs")
    recently_updated = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(confidence_score) FROM scholarships")
    avg_conf = cursor.fetchone()[0] or 0.0
    
    conn.close()
    return {
        "total_discovered": total,
        "verified": verified,
        "review_required": review_required,
        "active": active,
        "expired": expired,
        "recently_updated": recently_updated,
        "average_confidence": round(avg_conf, 1)
    }
