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


def save_user_research(analysis_id, interview_script, feedback_synthesis, personas):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_research (
            id TEXT PRIMARY KEY,
            analysis_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            interview_script TEXT,
            feedback_synthesis TEXT,
            personas TEXT
        )
    """)
    research_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO user_research (id, analysis_id, interview_script, feedback_synthesis, personas)
        VALUES (?, ?, ?, ?, ?)
    """, (research_id, analysis_id, interview_script, feedback_synthesis, personas))
    conn.commit()
    conn.close()
    return research_id

def get_user_research(analysis_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM user_research WHERE analysis_id = ? ORDER BY created_at DESC LIMIT 1", (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except:
        conn.close()
    return None

def save_backlog(analysis_id, backlog, sprint_plan):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backlogs (
            id TEXT PRIMARY KEY,
            analysis_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            backlog TEXT,
            sprint_plan TEXT
        )
    """)
    backlog_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO backlogs (id, analysis_id, backlog, sprint_plan)
        VALUES (?, ?, ?, ?)
    """, (backlog_id, analysis_id, backlog, sprint_plan))
    conn.commit()
    conn.close()
    return backlog_id

def get_backlog(analysis_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM backlogs WHERE analysis_id = ? ORDER BY created_at DESC LIMIT 1", (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except:
        conn.close()
    return None

def save_specs(analysis_id, design_brief, backend_spec, frontend_spec):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS specs (
            id TEXT PRIMARY KEY,
            analysis_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            design_brief TEXT,
            backend_spec TEXT,
            frontend_spec TEXT
        )
    """)
    spec_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO specs (id, analysis_id, design_brief, backend_spec, frontend_spec)
        VALUES (?, ?, ?, ?, ?)
    """, (spec_id, analysis_id, design_brief, backend_spec, frontend_spec))
    conn.commit()
    conn.close()
    return spec_id

def get_specs(analysis_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM specs WHERE analysis_id = ? ORDER BY created_at DESC LIMIT 1", (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except:
        conn.close()
    return None

def save_architecture(analysis_id, architecture, qa_plan, devops_plan):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS architecture (
            id TEXT PRIMARY KEY,
            analysis_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            architecture TEXT,
            qa_plan TEXT,
            devops_plan TEXT
        )
    """)
    arch_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO architecture (id, analysis_id, architecture, qa_plan, devops_plan)
        VALUES (?, ?, ?, ?, ?)
    """, (arch_id, analysis_id, architecture, qa_plan, devops_plan))
    conn.commit()
    conn.close()
    return arch_id

def get_architecture(analysis_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM architecture WHERE analysis_id = ? ORDER BY created_at DESC LIMIT 1", (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except:
        conn.close()
    return None

def save_generated_app(analysis_id, app_name, app_dir, status, files_generated, errors):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generated_apps (
            id TEXT PRIMARY KEY,
            analysis_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            app_name TEXT,
            app_dir TEXT,
            status TEXT,
            files_generated TEXT,
            errors TEXT
        )
    """)
    import json
    app_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO generated_apps (id, analysis_id, app_name, app_dir, status, files_generated, errors)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (app_id, analysis_id, app_name, app_dir, status, 
          json.dumps(files_generated), json.dumps(errors)))
    conn.commit()
    conn.close()
    return app_id

def get_generated_app(analysis_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM generated_apps WHERE analysis_id = ? ORDER BY created_at DESC LIMIT 1", (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except:
        conn.close()
    return None

def save_deployment(analysis_id, app_name, url, status, steps, errors):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deployments (
            id TEXT PRIMARY KEY,
            analysis_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            app_name TEXT,
            url TEXT,
            status TEXT,
            steps TEXT,
            errors TEXT
        )
    """)
    import json
    dep_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO deployments (id, analysis_id, app_name, url, status, steps, errors)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (dep_id, analysis_id, app_name, url, status,
          json.dumps(steps), json.dumps(errors)))
    conn.commit()
    conn.close()
    return dep_id

def get_deployment(analysis_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM deployments WHERE analysis_id = ? ORDER BY created_at DESC LIMIT 1", (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except:
        conn.close()
    return None

def save_frontend_code(analysis_id, app_name, frontend_dir, files_generated):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS frontend_code (
            id TEXT PRIMARY KEY,
            analysis_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            app_name TEXT,
            frontend_dir TEXT,
            files_generated TEXT
        )
    """)
    import json
    code_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO frontend_code (id, analysis_id, app_name, frontend_dir, files_generated)
        VALUES (?, ?, ?, ?, ?)
    """, (code_id, analysis_id, app_name, frontend_dir, json.dumps(files_generated)))
    conn.commit()
    conn.close()
    return code_id

def get_frontend_code(analysis_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM frontend_code WHERE analysis_id = ? ORDER BY created_at DESC LIMIT 1", (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except:
        conn.close()
    return None
