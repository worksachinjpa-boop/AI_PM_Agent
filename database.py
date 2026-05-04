import sqlite3
import uuid
from datetime import datetime

DB_PATH = "/root/ai-pm-agent/database.db"

def save_analysis(raw_idea, refined_problem, market_research, user_profile, validation):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    analysis_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO analyses (id, raw_idea, refined_problem, market_research, user_profile, validation)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (analysis_id, raw_idea, refined_problem, market_research, user_profile, validation))
    conn.commit()
    conn.close()
    return analysis_id

def get_analysis(analysis_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_all_analyses():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, created_at, raw_idea FROM analyses ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
