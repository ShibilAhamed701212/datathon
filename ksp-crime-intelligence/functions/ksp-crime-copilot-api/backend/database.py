import sqlite3
import os
from typing import Optional

_DATA_DIR = os.environ.get(
    "DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data")
)
DB_PATH = os.path.join(_DATA_DIR, "crime_data.sqlite")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query_firs(
    fir_id: Optional[int] = None,
    crime_type: Optional[str] = None,
    location: Optional[str] = None,
    district: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM firs WHERE 1=1"
    params = []
    if fir_id:
        sql += " AND fir_id = ?"
        params.append(fir_id)
    if crime_type:
        sql += " AND crime_type LIKE ?"
        params.append(f"%{crime_type}%")
    if location:
        sql += " AND location LIKE ?"
        params.append(f"%{location}%")
    if district:
        sql += " AND district LIKE ?"
        params.append(f"%{district}%")
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY date DESC LIMIT ?"
    params.append(limit)
    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def query_persons(person_id: Optional[int] = None, name: Optional[str] = None):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM persons WHERE 1=1"
    params = []
    if person_id:
        sql += " AND person_id = ?"
        params.append(person_id)
    if name:
        sql += " AND name LIKE ?"
        params.append(f"%{name}%")
    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def query_involvements(fir_id: Optional[int] = None, person_id: Optional[int] = None):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """SELECT i.*, p.name as person_name, p.role as person_role,
                    p.age, p.gender, p.address
             FROM involvement i
             JOIN persons p ON i.person_id = p.person_id
             WHERE 1=1"""
    params = []
    if fir_id:
        sql += " AND i.fir_id = ?"
        params.append(fir_id)
    if person_id:
        sql += " AND i.person_id = ?"
        params.append(person_id)
    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_stats_crimes_by_type():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT crime_type, COUNT(*) as count FROM firs GROUP BY crime_type ORDER BY count DESC"
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_stats_crimes_by_district():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT district, COUNT(*) as count FROM firs GROUP BY district ORDER BY count DESC"
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_stats_crimes_by_month():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT strftime('%Y-%m', date) as month, COUNT(*) as count
                      FROM firs GROUP BY month ORDER BY month""")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_stats_repeat_offenders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT p.person_id, p.name, p.age, p.gender, p.address,
                             COUNT(i.fir_id) as fir_count
                      FROM persons p
                      JOIN involvement i ON p.person_id = i.person_id
                      WHERE i.role = 'Accused'
                      GROUP BY p.person_id HAVING fir_count > 0
                      ORDER BY fir_count DESC""")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_all_descriptions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fir_id, description, crime_type, location FROM firs")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
