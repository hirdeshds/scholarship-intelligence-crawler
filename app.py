import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import init_db, get_all_scholarships, get_scholarship_by_id, get_stats
from seed_data import seed_database
from crawler import run_crawler_cycle

app = FastAPI(title="Scholarship Intelligence Crawler API")

init_db()
if not os.path.exists("scholarships.db"):
    seed_database()

@app.get("/api/stats")
def fetch_stats():
    return get_stats()

@app.get("/api/scholarships")
def list_scholarships(
    q: str = None,
    status: str = Query(None),
    source_type: str = Query(None),
    min_score: float = Query(None)
):
    return get_all_scholarships(query=q, status=status, source_type=source_type, min_score=min_score)

@app.get("/api/scholarships/{scholarship_id}")
def get_scholarship(scholarship_id: int):
    record = get_scholarship_by_id(scholarship_id)
    if not record:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return record

@app.post("/api/crawl")
def trigger_crawl():
    result = run_crawler_cycle()
    return result

@app.post("/api/seed")
def trigger_seed():
    seed_database()
    return {"status": "SUCCESS", "message": "Database reset and seeded with 22 authentic records"}

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")
