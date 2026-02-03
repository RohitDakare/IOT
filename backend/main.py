from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os
import uuid

app = FastAPI(title="Smart Pothole Detection API (SQLite Mode)")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "pothole_system.db"
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Initialize Database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS potholes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        latitude REAL,
        longitude REAL,
        depth REAL,
        severity_level TEXT,
        image_url TEXT,
        status TEXT DEFAULT 'Red',
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        repaired_at TIMESTAMP NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

class PotholeData(BaseModel):
    latitude: float
    longitude: float
    depth: float
    severity: str
    timestamp: float

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Allows dictionary-like access
    return conn

@app.post("/api/potholes")
async def report_pothole(data: PotholeData):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO potholes (latitude, longitude, depth, severity_level, status)
        VALUES (?, ?, ?, ?, 'Red')
        """
        cursor.execute(query, (data.latitude, data.longitude, data.depth, data.severity))
        conn.commit()
        pothole_id = cursor.lastrowid
        conn.close()
        return {"status": "success", "id": pothole_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload_image")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_name = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
            
        conn = get_db_connection()
        cursor = conn.cursor()
        # Correlate with last pothole
        cursor.execute("UPDATE potholes SET image_url = ? WHERE id = (SELECT MAX(id) FROM potholes)", (f"/uploads/{file_name}",))
        conn.commit()
        conn.close()
        
        return {"status": "success", "url": f"/uploads/{file_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/potholes")
async def get_potholes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM potholes")
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results

# Serve the uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Serve the Dashboard
if os.path.exists("../dashboard"):
    app.mount("/", StaticFiles(directory="../dashboard", html=True), name="dashboard")
elif os.path.exists("dashboard"):
    app.mount("/", StaticFiles(directory="dashboard", html=True), name="dashboard")

if __name__ == "__main__":
    import uvicorn
    print(f"Server starting in SQLITE mode. Database file: {DB_FILE}")
    print("Dashboard available at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
