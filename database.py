import sqlite3
import uuid
from datetime import datetime

DB_PATH = "/root/ai-pm-agent/database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            raw_idea TEXT,
            refined_problem TEXT,
            market_research TEXT,
            user_profile TEXT,
            validation TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prds (
            id TEXT PRIMARY KEY,
            analysis_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            prd TEXT,
            review TEXT,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

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

def save_prd(analysis_id, prd, review):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    prd_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO prds (id, analysis_id, prd, review)
        VALUES (?, ?, ?, ?)
    """, (prd_id, analysis_id, prd, review))
    conn.commit()
    conn.close()
    return prd_id

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

def get_prd(analysis_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prds WHERE analysis_id = ? ORDER BY created_at DESC LIMIT 1", (analysis_id,))
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
