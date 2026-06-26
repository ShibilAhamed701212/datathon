import os
import sys
import uvicorn
import sqlite3
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.wsgi import WSGIMiddleware

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DATA_DIR", "/tmp/data")
os.environ.setdefault("LLM_MODE", "mock")

data_dir = os.environ["DATA_DIR"]
os.makedirs(data_dir, exist_ok=True)

DB_PATH = os.path.join(data_dir, "crime_data.sqlite")


def ensure_database():
    if os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS firs (fir_id INTEGER PRIMARY KEY, date TEXT, crime_type TEXT, description TEXT, location TEXT, district TEXT, status TEXT);
        CREATE TABLE IF NOT EXISTS persons (person_id INTEGER PRIMARY KEY, name TEXT, role TEXT, age INTEGER, gender TEXT, address TEXT, district TEXT);
        CREATE TABLE IF NOT EXISTS involvement (involvement_id INTEGER PRIMARY KEY AUTOINCREMENT, fir_id INTEGER, person_id INTEGER, role TEXT, FOREIGN KEY(fir_id) REFERENCES firs(fir_id), FOREIGN KEY(person_id) REFERENCES persons(person_id));
    """)
    firs = [
        (
            101,
            "2026-01-10",
            "Theft",
            "Car stolen from parking lot near MG Road",
            "MG Road, Bengaluru",
            "Bengaluru Urban",
            "Open",
        ),
        (
            102,
            "2026-01-12",
            "Burglary",
            "House break-in near Mysore Palace",
            "Mysore Palace Road, Mysuru",
            "Mysuru",
            "Closed",
        ),
        (
            103,
            "2026-01-15",
            "Assault",
            "Man attacked on MG Road",
            "MG Road, Bengaluru",
            "Bengaluru Urban",
            "Open",
        ),
        (
            104,
            "2026-01-20",
            "Theft",
            "Pickpocketing at Banashankari",
            "Banashankari, Bengaluru",
            "Bengaluru Urban",
            "Closed",
        ),
        (
            105,
            "2026-02-05",
            "Vehicle Theft",
            "Two-wheeler stolen from Mall of Mysuru",
            "Mall of Mysuru, Mysuru",
            "Mysuru",
            "Open",
        ),
        (
            106,
            "2026-02-10",
            "Fraud",
            "Online fraud, victim duped of Rs 50,000",
            "Jayanagar, Bengaluru",
            "Bengaluru Urban",
            "Open",
        ),
        (
            107,
            "2026-02-18",
            "Burglary",
            "Shop break-in at KR Market",
            "KR Market, Bengaluru",
            "Bengaluru Urban",
            "Open",
        ),
        (
            108,
            "2026-03-01",
            "Assault",
            "Road rage incident on NH-75",
            "NH-75, Tumkur",
            "Tumkur",
            "Closed",
        ),
        (
            109,
            "2026-03-05",
            "Theft",
            "Bicycle theft at Vidhana Soudha",
            "Vidhana Soudha, Bengaluru",
            "Bengaluru Urban",
            "Open",
        ),
        (
            110,
            "2026-03-10",
            "Robbery",
            "Bus robbery at Majestic",
            "Majestic, Bengaluru",
            "Bengaluru Urban",
            "Open",
        ),
        (
            111,
            "2026-03-12",
            "Vehicle Theft",
            "Car stolen from BTM Layout",
            "BTM Layout, Bengaluru",
            "Bengaluru Urban",
            "Open",
        ),
        (
            112,
            "2026-03-15",
            "Fraud",
            "Bank fraud in Mangaluru",
            "Mangaluru",
            "Dakshina Kannada",
            "Open",
        ),
        (
            113,
            "2026-03-18",
            "Burglary",
            "Flat burglary in Indiranagar",
            "Indiranagar, Bengaluru",
            "Bengaluru Urban",
            "Closed",
        ),
        (
            114,
            "2026-03-20",
            "Assault",
            "Chain snatching in Hubli",
            "Hubli",
            "Dharwad",
            "Open",
        ),
        (
            115,
            "2026-04-01",
            "Theft",
            "Luggage theft at Yeshwanthpur",
            "Yeshwanthpur, Bengaluru",
            "Bengaluru Urban",
            "Open",
        ),
    ]
    persons = [
        (
            1,
            "Ravi Kumar",
            "Victim",
            45,
            "Male",
            "MG Road, Bengaluru",
            "Bengaluru Urban",
        ),
        (2, "Aisha Khan", "Accused", 30, "Female", "Mysuru City", "Mysuru"),
        (
            3,
            "Manjunath Gowda",
            "Victim",
            50,
            "Male",
            "Banashankari, Bengaluru",
            "Bengaluru Urban",
        ),
        (
            4,
            "Suresh Reddy",
            "Accused",
            25,
            "Male",
            "Koramangala, Bengaluru",
            "Bengaluru Urban",
        ),
        (
            5,
            "Lakshmi Devi",
            "Victim",
            35,
            "Female",
            "Jayanagar, Bengaluru",
            "Bengaluru Urban",
        ),
        (
            6,
            "Venkatesh Rao",
            "Accused",
            42,
            "Male",
            "Malleshwaram, Bengaluru",
            "Bengaluru Urban",
        ),
        (
            7,
            "Priya Sharma",
            "Victim",
            28,
            "Female",
            "Indiranagar, Bengaluru",
            "Bengaluru Urban",
        ),
        (
            8,
            "Ahmed Hussain",
            "Accused",
            38,
            "Male",
            "Majestic, Bengaluru",
            "Bengaluru Urban",
        ),
        (
            9,
            "Kiran P",
            "Witness",
            33,
            "Male",
            "BTM Layout, Bengaluru",
            "Bengaluru Urban",
        ),
        (10, "Sunita Patil", "Victim", 55, "Female", "Hubli", "Dharwad"),
        (11, "Ramesh Shetty", "Accused", 29, "Male", "Mangaluru", "Dakshina Kannada"),
        (12, "Anitha K", "Victim", 40, "Female", "Tumkur", "Tumkur"),
        (
            13,
            "Deepak Jain",
            "Victim",
            32,
            "Male",
            "KR Market, Bengaluru",
            "Bengaluru Urban",
        ),
        (14, "Mohan Das", "Witness", 60, "Male", "Mysuru City", "Mysuru"),
        (
            15,
            "Kavitha N",
            "Victim",
            27,
            "Female",
            "Vidhana Soudha, Bengaluru",
            "Bengaluru Urban",
        ),
        (
            16,
            "Siddharth M",
            "Accused",
            35,
            "Male",
            "Yeshwanthpur, Bengaluru",
            "Bengaluru Urban",
        ),
        (
            17,
            "Geetha R",
            "Victim",
            48,
            "Female",
            "BTM Layout, Bengaluru",
            "Bengaluru Urban",
        ),
        (18, "Prakash B", "Accused", 22, "Male", "Mysuru City", "Mysuru"),
        (19, "Naveen Kumar", "Victim", 31, "Male", "Hubli", "Dharwad"),
        (
            20,
            "Shweta M",
            "Witness",
            26,
            "Female",
            "Indiranagar, Bengaluru",
            "Bengaluru Urban",
        ),
    ]
    involvement = [
        (101, 1, "Victim"),
        (101, 2, "Accused"),
        (102, 14, "Victim"),
        (102, 18, "Accused"),
        (103, 3, "Victim"),
        (103, 4, "Accused"),
        (104, 3, "Victim"),
        (104, 4, "Accused"),
        (105, 2, "Victim"),
        (105, 18, "Accused"),
        (106, 5, "Victim"),
        (106, 6, "Accused"),
        (107, 13, "Victim"),
        (107, 6, "Accused"),
        (108, 12, "Victim"),
        (109, 15, "Victim"),
        (109, 16, "Accused"),
        (110, 8, "Accused"),
        (110, 7, "Victim"),
        (111, 17, "Victim"),
        (111, 16, "Accused"),
        (112, 5, "Victim"),
        (112, 11, "Accused"),
        (113, 7, "Victim"),
        (114, 10, "Victim"),
        (114, 19, "Victim"),
        (115, 15, "Victim"),
        (115, 16, "Accused"),
    ]
    cursor.executemany("INSERT OR REPLACE INTO firs VALUES (?,?,?,?,?,?,?)", firs)
    cursor.executemany("INSERT OR REPLACE INTO persons VALUES (?,?,?,?,?,?,?)", persons)
    cursor.executemany(
        "INSERT INTO involvement VALUES (?,?,?,?)",
        [(i + 1, *r) for i, r in enumerate(involvement)],
    )
    conn.commit()
    conn.close()


ensure_database()

# Run the backend app directly - it has /api/ prefix on all routes
from backend.app import app

# Serve static frontend at root
static_dir = os.path.join(PROJECT_ROOT, "frontend", "static")
if os.path.exists(static_dir):

    @app.get("/")
    async def serve_root():
        return FileResponse(os.path.join(static_dir, "index.html"))

    @app.exception_handler(404)
    async def spa_fallback(req, exc):
        path = req.url.path
        if not path.startswith("/api/") and static_dir:
            index_path = os.path.join(static_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
        return JSONResponse({"error": "Not found"}, status_code=404)


if __name__ == "__main__":
    port = int(
        os.environ.get("X_ZOHO_CATALYST_LISTEN_PORT", os.environ.get("PORT", 9000))
    )
    uvicorn.run(app, host="0.0.0.0", port=port)
