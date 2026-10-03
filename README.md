# Atlas Funding — Scholarship Intelligence Engine

Automated, continuous web crawler and evidence-based verification engine designed to discover, extract, verify, score, and track authentic educational funding opportunities for Indian students.

---

## Executive Overview

The **Scholarship Intelligence Engine** maintains a normalized, real-time repository of verified Indian scholarship opportunities across central/state government portals, corporate CSR initiatives, educational trusts, and higher education institutions.

The engine automates the entire lifecycle:

`Discovery -> Crawling -> Schema Extraction -> Primary Verification -> Math Scoring -> Change Tracking -> Persistence -> Real-time API & Dashboard`

---

## Core Architecture & Innovations

### 1. Multi-Tier Primary Source Verification
To ensure high accuracy, the engine differentiates between official primary source providers and third-party aggregators. Sources are evaluated against an enterprise domain registry:
- **Government**: Portals under `.gov.in`, `.nic.in`
- **Universities & Academic Institutions**: Domains under `.ac.in`, `.edu.in`
- **Corporate CSR**: Direct corporate domain CSR initiatives (e.g. Tata Capital, Reliance Foundation, HDFC Bank, SBI Foundation)
- **Foundations & Trusts**: Non-profit academic endowments (e.g. JN Tata Endowment, Narotam Sekhsaria Foundation)
- **Aggregators**: Secondary blogs or forums (automatically tagged low confidence)

### 2. Deterministic Confidence Scoring Engine
Confidence scores are calculated using an explicit, non-generative mathematical formula:

$$Score = S_{\text{domain}} + S_{\text{app\_link}} + S_{\text{reachability}} + S_{\text{evidence}} + S_{\text{consistency}}$$

- **Primary Domain Match ($S_{\text{domain}}$)**: $+35.0\%$ for verified primary domains.
- **Direct Application Link ($S_{\text{app\_link}}$)**: $+20.0\%$ for direct application URLs.
- **Endpoint Reachability ($S_{\text{reachability}}$)**: $+15.0\%$ for responsive HTTP endpoints.
- **Traceable Text Evidence ($S_{\text{evidence}}$)**: $+20.0\%$ for verified textual evidence snippets.
- **Field Consistency ($S_{\text{consistency}}$)**: $+10.0\%$ for complete, non-contradictory metadata.

#### Threshold Policy
- **`VERIFIED`**: Confidence score $\ge 95.0\%$
- **`REVIEW REQUIRED`**: Confidence score $< 95.0\%$

### 3. Anti-Hallucination & Traceability Pipeline
- **Zero Field Fabrication**: Unmentioned criteria default to `"Not specified"`.
- **Source Snippet Auditing**: Every record retains verbatim text evidence extracted from primary sources.

### 4. Differential Audit Trail & Change Detection
Re-crawling active records detects field-level modifications (such as extended deadlines or updated benefits). Changes are stored in `change_logs` with old value, new value, detection timestamp, source URL, and supporting evidence.

### 5. Automated Lifecycle State Machine
Dynamic status assignment based on verification and date checks:
- **`ACTIVE`**: Verified source and valid deadline.
- **`EXPIRING_SOON`**: Deadline within 15 days of current date.
- **`EXPIRED`**: Deadline past current date.
- **`NO_LONGER_VERIFIABLE`**: Primary source URL non-responsive or retired.

---

## System Design & Data Flow

```
+------------------+     +-------------------+     +---------------------+
|  Seed Sources &  | --> |  HTML Scraper &   | --> | Standardized Schema |
| Official Portals |     | BeautifulSoup4    |     | Field Normalizer    |
+------------------+     +-------------------+     +---------------------+
                                                              |
                                                              v
+------------------+     +-------------------+     +---------------------+
| Real-time API &  | <-- | SQLite Store &    | <-- | Verification Engine |
| Web Dashboard    |     | Change Audit Logs |     | & Math Scoring      |
+------------------+     +-------------------+     +---------------------+
```

---

## Normalized Schema Specification

The engine normalizes unstructured HTML into a standard 22-field schema:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Primary title of the scholarship |
| `provider` | TEXT | Department, ministry, foundation, or company offering funding |
| `official_source_url` | TEXT | Canonical primary URL |
| `application_url` | TEXT | Direct portal link for student application |
| `source_type` | TEXT | Government, Corporate CSR, Foundation / Trust, University |
| `amount` | TEXT | Monetary financial benefit or tuition fee coverage |
| `eligibility` | TEXT | High-level summary of eligibility |
| `academic_reqs` | TEXT | Minimum marks or academic qualification required |
| `course_level` | TEXT | Education level (Class 10/12, UG, PG, Diploma, Ph.D.) |
| `income_criteria` | TEXT | Maximum annual family income cap |
| `age_criteria` | TEXT | Age limits or constraints |
| `gender_criteria` | TEXT | Gender-specific criteria |
| `category_criteria` | TEXT | Reservation category criteria (General, SC, ST, OBC, PwD, EWS) |
| `domicile_reqs` | TEXT | State or national domicile requirements |
| `institution_reqs` | TEXT | Approved university/college criteria |
| `opening_date` | TEXT | Application window opening date |
| `closing_date` | TEXT | Application deadline |
| `documents_req` | TEXT | Required documentation list |
| `selection_process` | TEXT | Selection methodology |
| `renewal_reqs` | TEXT | Annual continuation criteria |
| `status` | TEXT | VERIFIED, REVIEW_REQUIRED, EXPIRED, EXPIRING_SOON, NO_LONGER_VERIFIABLE |
| `confidence_score` | REAL | Calculated score ($0.0\%$ to $100.0\%$) |
| `evidence_text` | TEXT | Textual snippet captured from source |

---

## Directory Structure

```
scholarship-intelligence-crawler/
├── app.py              # FastAPI server & REST API router
├── crawler.py          # Continuous crawling & extraction cycle
├── database.py         # SQLite persistence & query management
├── verifier.py         # Deterministic scoring & verification engine
├── tracker.py          # Change detection & lifecycle state machine
├── seed_data.py        # Seed dataset (22 authentic records)
├── requirements.txt    # Production Python dependencies
├── README.md           # Enterprise product documentation
├── TECHNICAL_NOTE.md   # Architectural & methodology document
└── static/
    ├── index.html      # Glassmorphic web dashboard UI
    ├── style.css       # Production CSS design system
    └── app.js          # REST API integration & modal handler
```

---

## Installation & Operation Guide

### Prerequisites
- Python 3.10+
- SQLite 3

### 1. Environment Setup
Clone the repository and install core dependencies:

```bash
git clone https://github.com/organization/scholarship-intelligence-crawler.git
cd scholarship-intelligence-crawler
pip install -r requirements.txt
```

### 2. Initialize & Seed Database
Initialize SQLite database (`scholarships.db`) and seed initial verified records:

```bash
python seed_data.py
```

### 3. Launch Web Server & Dashboard
Start the production server using Uvicorn:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Open the web interface in your browser:
```
http://127.0.0.1:8000
```

---

## REST API Reference

### 1. Get Dashboard Statistics
`GET /api/stats`

**Response:**
```json
{
  "total_discovered": 22,
  "verified": 17,
  "review_required": 5,
  "active": 18,
  "expired": 1,
  "recently_updated": 2,
  "average_confidence": 94.2
}
```

### 2. Search & Filter Scholarships
`GET /api/scholarships?q=tata&status=VERIFIED&source_type=Corporate%20CSR`

### 3. Get Scholarship Details & Audit Trail
`GET /api/scholarships/{id}`

### 4. Trigger Crawler Cycle
`POST /api/crawl`

### 5. Reset Seed Database
`POST /api/seed`

---

## Summary Metrics

- **Total Records Managed**: 22 authentic opportunities
- **Primary Verified Records ($\ge 95.0\%$)**: 17 records
- **Source Tiers Represented**: Government, Corporate CSR, Foundation / Trust, University
- **Change Log Coverage**: Historical audit trail active
- **Expired/Stale Lifecycle Handling**: Automated status management active
