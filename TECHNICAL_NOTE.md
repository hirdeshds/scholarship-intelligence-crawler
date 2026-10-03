# Technical Note: Scholarship Intelligence Crawler

## System Architecture

The Scholarship Intelligence Crawler is designed to continuously discover, extract, verify, score, store, and update authentic scholarship opportunities for Indian students. The pipeline operates as a deterministic, multi-stage automated system.

```
Discovery Engine -> Source Classification -> Unstructured Extraction -> Evidence Verification -> Math Confidence Scoring -> Change Detection & Stale Evaluation -> Database Persistence -> Real-time UI Dashboard
```

## Technology Stack

- **Backend Runtime**: Python 3.10+ with FastAPI and Uvicorn
- **Database Layer**: SQLite 3 with WAL mode and normalized schema
- **Crawler & Parsing**: Requests HTTP client and BeautifulSoup4 DOM parser
- **Frontend Dashboard**: Vanilla HTML5, Modern Glassmorphic CSS3, Vanilla JavaScript (ES6+)

## Discovery & Classification Methodology

Discovery operates on a dynamic crawler model:
1. **Seed Discovery**: Portal seeds monitor central government portals (NSP, AICTE, UGC), state government portals (MahaDBT, SVMCM West Bengal, Punjab Scholarship Portal), corporate CSR initiatives (Tata Capital, Reliance Foundation, HDFC Parivartan, SBI Foundation), and top universities (IIT Bombay, DU, Pune University).
2. **Source Classification**: Incoming URLs are categorized into five distinct tiers:
   - **Government**: Portals under `.gov.in`, `.nic.in`
   - **Corporate CSR**: Direct corporate domain CSR initiatives
   - **Foundation / Trust**: Non-profit academic endowments
   - **University**: Higher educational institution domains under `.ac.in`, `.edu.in`
   - **Aggregator**: External blogs or news portals (tagged low confidence)

## Extraction Methodology

Unstructured web data is parsed into a 22-field standard schema:
- **Core Identifiers**: Name, Provider, Official Source URL, Application Link, Source Type
- **Benefit & Eligibility**: Scholarship Amount, Eligibility Overview, Academic Requirements, Course Level, Income Criteria, Age Limit, Gender Eligibility, Category Criteria, Domicile Requirements, Institution Requirements
- **Lifecycle Data**: Opening Date, Closing Date, Documents Required, Selection Process, Renewal Criteria, System Status, Confidence Score

Regex pattern matchers extract monetary figures, income thresholds, and date formats.

## Verification & Deterministic Confidence Engine

To avoid hallucination or arbitrary AI scoring, the verification engine applies a deterministic mathematical formula:

$$Score = S_{domain} + S_{app\_link} + S_{reachability} + S_{evidence} + S_{consistency}$$

- **Primary Domain Match ($S_{domain}$)**: +35.0% if source domain matches `.gov.in`, `.nic.in`, `.ac.in`, `.edu.in`, or recognized corporate/foundation registry.
- **Direct Application Link ($S_{app\_link}$)**: +20.0% if valid application URL is active.
- **Endpoint Reachability ($S_{reachability}$)**: +15.0% if HTTP status returns success.
- **Traceable Evidence ($S_{evidence}$)**: +20.0% if source HTML snippet contains verifiable textual proof.
- **Field Consistency ($S_{consistency}$)**: +10.0% if closing date and financial benefit are explicitly defined.

### Verification Threshold Rule
- **VERIFIED**: System confidence score $\ge 95.0\%$
- **REVIEW REQUIRED**: System confidence score $< 95.0\%$

## Anti-Hallucination Framework

1. **Strict Fallback Policy**: Any unmentioned field is normalized to `"Not specified"`. The system never generates dummy estimates.
2. **Traceable Evidence Snippets**: Every scholarship record retains raw source text snippets.
3. **Primary vs Aggregator Separation**: Third-party blogs receive zero domain verification weight.

## Change Detection & Stale Data Mechanics

1. **Audit Trail Logging**: When a crawl cycle detects altered field values (e.g. deadline extension), a record is logged into `change_logs` storing field name, old value, new value, timestamp, source URL, and evidence.
2. **Lifecycle Status Rules**:
   - **ACTIVE**: Valid deadline and verified status.
   - **EXPIRING_SOON**: Deadline within 15 days of current date.
   - **EXPIRED**: Closing date past current system date.
   - **NO_LONGER_VERIFIABLE**: Primary source URL returns 404 or connection failure.
