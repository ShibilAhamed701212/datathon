import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import sqlite3
from backend import database

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crime_data.sqlite")

def test_database_exists():
    assert os.path.exists(DB_PATH), "Database file not found. Run data/generate_data.py first."

def test_database_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    assert "firs" in tables, "firs table missing"
    assert "persons" in tables, "persons table missing"
    assert "involvement" in tables, "involvement table missing"

def test_firs_have_data():
    firs = database.query_firs()
    assert len(firs) > 0, "No FIRs found"
    assert len(firs) >= 15, f"Expected >= 15 FIRs, got {len(firs)}"

def test_query_firs_by_crime_type():
    results = database.query_firs(crime_type="Theft")
    assert len(results) >= 1
    for r in results:
        assert "Theft" in r["crime_type"] or "theft" in r["crime_type"].lower()

def test_query_firs_by_location():
    results = database.query_firs(location="MG Road")
    assert len(results) >= 1

def test_query_firs_by_status():
    open_cases = database.query_firs(status="Open")
    closed_cases = database.query_firs(status="Closed")
    assert len(open_cases) >= 1
    assert len(closed_cases) >= 1

def test_stats_crimes_by_type():
    stats = database.get_stats_crimes_by_type()
    assert len(stats) >= 1
    total = sum(s["count"] for s in stats)
    assert total >= 15

def test_stats_crimes_by_district():
    stats = database.get_stats_crimes_by_district()
    assert len(stats) >= 1

def test_stats_crimes_by_month():
    stats = database.get_stats_crimes_by_month()
    assert len(stats) >= 1

def test_stats_repeat_offenders():
    stats = database.get_stats_repeat_offenders()
    for s in stats:
        assert s["fir_count"] >= 1

def test_query_persons():
    persons = database.query_persons()
    assert len(persons) >= 20

def test_query_persons_by_name():
    results = database.query_persons(name="Ravi")
    assert len(results) >= 1

def test_involvements():
    invs = database.query_involvements(fir_id=101)
    assert len(invs) >= 1
    for inv in invs:
        assert inv["fir_id"] == 101

def test_rag_retrieve_context():
    from backend import rag_utils
    rag_utils.initialize_index()
    results = rag_utils.retrieve_context("Car stolen in Bangalore", k=3)
    assert len(results) <= 3

def test_rag_generate_answer_mock():
    from backend import rag_utils
    rag_utils.initialize_index()
    results = rag_utils.retrieve_context("Vehicle theft in Mysuru", k=2)
    answer = rag_utils.generate_answer("Vehicle theft in Mysuru", results, llm_mode="mock")
    assert len(answer) > 0
    assert "FIR" in answer or "Based on the crime records" in answer or "I couldn't find" in answer

def test_graph_build():
    from backend import graph
    result = graph.build_crime_graph(limit=5)
    assert "nodes" in result
    assert "edges" in result
    assert len(result["nodes"]) >= 1
