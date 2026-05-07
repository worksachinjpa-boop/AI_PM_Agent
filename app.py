from fastapi import FastAPI, Request, Cookie
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse, PlainTextResponse
import asyncio
import json
import sys
import os

sys.path.insert(0, "/root/ai-pm-agent")
os.chdir("/root/ai-pm-agent")

from dotenv import load_dotenv
load_dotenv()

from agents.idea_refiner import run_idea_refiner
from agents.market_researcher import run_market_researcher
from agents.user_identifier import run_user_identifier
from agents.validator import run_validator
from database import save_analysis, get_analysis, get_all_analyses, save_prd, get_prd

app = FastAPI()
APP_PASSWORD = os.getenv("APP_PASSWORD", "admin123")

def event(agent, status, **kwargs):
    data = {"agent": agent, "status": status}
    data.update(kwargs)
    return "data: " + json.dumps(data) + "\n\n"

def is_authenticated(session=None):
    return session == APP_PASSWORD

def base_style():
    return """<style>
    body{font-family:sans-serif;background:#0f0f0f;color:#e0e0e0;margin:0}
    .header{background:#1a1a2e;padding:24px 40px;display:flex;align-items:center;justify-content:space-between}
    .header h1{color:#7c6fcd;font-size:24px;margin:0}
    .container{max-width:900px;margin:40px auto;padding:0 20px}
    .card{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:24px;margin-bottom:20px}
    .card h2{color:#7c6fcd;font-size:16px;margin:0 0 12px}
    .card p{font-size:14px;color:#ccc;line-height:1.7;white-space:pre-wrap;margin:0}
    .agent{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:20px;margin-bottom:16px}
    .agent.running{border-color:#7c6fcd}.agent.done{border-color:#2a5a3a}
    .atitle{font-weight:600;font-size:15px;margin-bottom:6px}
    .astatus{font-size:12px;color:#888}.astatus.running{color:#7c6fcd}.astatus.done{color:#4caf7d}
    .btn{background:#7c6fcd;color:white;border:none;padding:12px 24px;border-radius:8px;font-size:15px;cursor:pointer;text-decoration:none;display:inline-block;margin-right:10px;margin-bottom:10px}
    .btn:disabled{background:#444;cursor:not-allowed}
    .btn-green{background:#2a5a3a}
    a.link{color:#7c6fcd;text-decoration:none;font-size:14px}
    </style>"""

LOGIN_HTML = """<!DOCTYPE html><html><head><title>AI Product Manager</title>
<style>body{font-family:sans-serif;background:#0f0f0f;color:#e0e0e0;margin:0;display:flex;align-items:center;justify-content:center;min-height:100vh}
.card{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:16px;padding:48px;width:100%;max-width:400px}
h1{color:#7c6fcd;font-size:22px;margin:0 0 8px}p{color:#888;font-size:14px;margin:0 0 32px}
input{width:100%;background:#0f0f0f;border:1px solid #333;border-radius:8px;padding:12px 14px;color:#e0e0e0;font-size:15px;outline:none;box-sizing:border-box;margin-bottom:16px}
input:focus{border-color:#7c6fcd}button{width:100%;background:#7c6fcd;color:white;border:none;padding:12px;border-radius:8px;font-size:15px;cursor:pointer}
.error{color:#e24b4a;font-size:13px;margin-top:12px;text-align:center}</style></head>
<body><div class="card"><h1>AI Product Manager</h1><p>Enter password to continue</p>
<form method="POST" action="/login"><input type="password" name="password" placeholder="Password" autofocus/>
<button type="submit">Login</button></form><div class="error"></div></div></body></html>"""

LOGIN_ERROR_HTML = LOGIN_HTML.replace('<div class="error"></div>', '<div class="error">Incorrect password.</div>')

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse(content=LOGIN_HTML)

@app.post("/login")
async def login(request: Request):
    form = await request.form()
    password = form.get("password", "")
    if password == APP_PASSWORD:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="session", value=APP_PASSWORD, httponly=True)
        return response
    return HTMLResponse(content=LOGIN_ERROR_HTML)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session")
    return response

@app.get("/", response_class=HTMLResponse)
async def home(session: str = Cookie(default=None)):
    if not is_authenticated(session):
        return RedirectResponse(url="/login", status_code=302)
    with open("/root/ai-pm-agent/templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/history", response_class=HTMLResponse)
async def history(session: str = Cookie(default=None)):
    if not is_authenticated(session):
        return RedirectResponse(url="/login", status_code=302)
    analyses = get_all_analyses()
    rows = ""
    for a in analyses:
        preview = a["raw_idea"][:80] + "..." if len(a["raw_idea"]) > 80 else a["raw_idea"]
        rows += "<div style=\"background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:16px;margin-bottom:12px\">"
        rows += "<div style=\"font-size:12px;color:#888;margin-bottom:6px\">" + str(a["created_at"]) + " | ID: " + a["id"] + "</div>"
        rows += "<div style=\"font-size:14px;color:#ccc;margin-bottom:10px\">" + preview + "</div>"
        rows += "<a href=\"/result/" + a["id"] + "\" class=\"btn\">View Analysis</a>"
        rows += "</div>"
    if not rows:
        rows = "<p style=\"color:#888\">No analyses yet.</p>"
    html = "<!DOCTYPE html><html><head><title>History</title>" + base_style() + "</head>"
    html += "<body><div class=\"header\"><h1>Analysis History</h1><a href=\"/logout\" style=\"color:#888;font-size:13px\">Logout</a></div>"
    html += "<div class=\"container\"><a class=\"link\" href=\"/\">&larr; Back</a><div style=\"margin-top:24px\">" + rows + "</div></div></body></html>"
    return HTMLResponse(content=html)

@app.get("/result/{analysis_id}", response_class=HTMLResponse)
async def result(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        return RedirectResponse(url="/login", status_code=302)
    data = get_analysis(analysis_id)
    if not data:
        return HTMLResponse(content="<h1>Not found</h1>", status_code=404)
    def section(title, content):
        return "<div class=\"card\"><h2>" + title + "</h2><p>" + str(content) + "</p></div>"
    html = "<!DOCTYPE html><html><head><title>Analysis Result</title>" + base_style() + "</head>"
    html += "<body><div class=\"header\"><h1>Analysis Result</h1><a href=\"/logout\" style=\"color:#888;font-size:13px\">Logout</a></div>"
    html += "<div class=\"container\"><a class=\"link\" href=\"/history\">&larr; History</a><div style=\"margin-top:24px\">"
    html += section("Raw Idea", data["raw_idea"])
    html += section("Refined Problem", data["refined_problem"])
    html += section("Market Research", data["market_research"])
    html += section("User Profile", data["user_profile"])
    html += section("Validation", data["validation"])
    html += "<div style=\"margin-top:24px;padding-top:24px;border-top:1px solid #2a2a2a\">"
    html += "<a href=\"/research/" + analysis_id + "\" class=\"btn\">Run User Research</a>"
    html += "<a href=\"/prd/" + analysis_id + "\" class=\"btn btn-green\">Generate PRD</a>"
    html += "<a href=\"/backlog/" + analysis_id + "\" style=\"background:#1a3a5a;color:#4a9eff;padding:12px 24px;border-radius:8px;font-size:15px;text-decoration:none;margin-right:10px;margin-bottom:10px;display:inline-block\">Create Backlog</a>"
    html += "<a href=\"/specs/" + analysis_id + "\" style=\"background:#3a1a5a;color:#aa4aff;padding:12px 24px;border-radius:8px;font-size:15px;text-decoration:none;margin-right:10px;margin-bottom:10px;display:inline-block\">Run Parallel Specs</a>"
    html += "<a href=\"/architecture/" + analysis_id + "\" style=\"background:#1a3a2a;color:#4aff9f;padding:12px 24px;border-radius:8px;font-size:15px;text-decoration:none;margin-right:10px;margin-bottom:10px;display:inline-block\">System Architecture</a>"
    html += "</div></div></div></body></html>"
    return HTMLResponse(content=html)

@app.get("/research/{analysis_id}", response_class=HTMLResponse)
async def research_page(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        return RedirectResponse(url="/login", status_code=302)
    analysis = get_analysis(analysis_id)
    if not analysis:
        return HTMLResponse(content="<h1>Not found</h1>", status_code=404)
    from database import get_user_research
    existing = get_user_research(analysis_id)
    interview = existing["interview_script"] if existing else ""
    feedback = existing["feedback_synthesis"] if existing else ""
    personas = existing["personas"] if existing else ""
    html = "<!DOCTYPE html><html><head><title>User Research</title>" + base_style() + "</head>"
    html += "<body><div class=\"header\"><h1>User Research</h1><a href=\"/logout\" style=\"color:#888;font-size:13px\">Logout</a></div>"
    html += "<div class=\"container\"><a class=\"link\" href=\"/result/" + analysis_id + "\">&larr; Back</a><div style=\"margin-top:24px\">"
    html += "<button class=\"btn\" id=\"genbtn\" onclick=\"generateResearch('" + analysis_id + "')\">Generate User Research</button>"
    html += "<div id=\"agents\">"
    html += "<div class=\"agent\" id=\"card-interview\"><div class=\"atitle\">1. Interview Script Generator</div><div class=\"astatus\" id=\"status-interview\">Waiting</div></div>"
    html += "<div class=\"agent\" id=\"card-feedback\"><div class=\"atitle\">2. Feedback Synthesizer</div><div class=\"astatus\" id=\"status-feedback\">Waiting</div></div>"
    html += "<div class=\"agent\" id=\"card-persona\"><div class=\"atitle\">3. Persona Builder</div><div class=\"astatus\" id=\"status-persona\">Waiting</div></div>"
    html += "</div>"
    html += "<div class=\"card\"><h2>Interview Script</h2><p id=\"interview-content\">" + interview + "</p></div>"
    html += "<div class=\"card\"><h2>Feedback Synthesis</h2><p id=\"feedback-content\">" + feedback + "</p></div>"
    html += "<div class=\"card\"><h2>User Personas</h2><p id=\"persona-content\">" + personas + "</p></div>"
    html += "</div></div>"
    html += """<script>
async function generateResearch(id) {
    const btn = document.getElementById("genbtn");
    btn.disabled = true; btn.textContent = "Generating...";
    ["interview","feedback","persona"].forEach(a => {
        document.getElementById("card-"+a).className = "agent";
        document.getElementById("status-"+a).textContent = "Waiting";
        document.getElementById("status-"+a).className = "astatus";
    });
    const res = await fetch("/generate-research/"+id, {method:"POST"});
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    while(true) {
        const {done, value} = await reader.read();
        if(done) break;
        const lines = dec.decode(value).split("\n").filter(l => l.startsWith("data: "));
        for(const line of lines) {
            try {
                const d = JSON.parse(line.slice(6));
                if(d.agent === "complete") { btn.disabled=false; btn.textContent="Regenerate Research"; continue; }
                if(d.agent === "error") { btn.disabled=false; btn.textContent="Generate User Research"; alert(d.message); continue; }
                const card = document.getElementById("card-"+d.agent);
                const status = document.getElementById("status-"+d.agent);
                if(d.status === "running") { card.className="agent running"; status.className="astatus running"; status.textContent=d.message; }
                if(d.status === "done" && d.result) {
                    card.className="agent done"; status.className="astatus done"; status.textContent="Complete";
                    if(d.agent === "interview") document.getElementById("interview-content").textContent = d.result;
                    if(d.agent === "feedback") document.getElementById("feedback-content").textContent = d.result;
                    if(d.agent === "persona") document.getElementById("persona-content").textContent = d.result;
                }
            } catch(e) {}
        }
    }
}
</script></body></html>"""
    return HTMLResponse(content=html)

@app.post("/generate-research/{analysis_id}")
async def generate_research(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        async def deny():
            yield event("error", "error", message="Not authenticated.")
        return StreamingResponse(deny(), media_type="text/event-stream")
    analysis = get_analysis(analysis_id)
    if not analysis:
        async def not_found():
            yield event("error", "error", message="Analysis not found.")
        return StreamingResponse(not_found(), media_type="text/event-stream")

    async def generate():
        try:
            yield event("interview", "running", message="Generating interview script...")
            from agents.interview_generator import run_interview_generator
            interview = await asyncio.to_thread(run_interview_generator, analysis)
            yield event("interview", "done", result=interview)

            yield event("feedback", "running", message="Synthesizing user feedback...")
            from agents.feedback_synthesizer import run_feedback_synthesizer
            feedback = await asyncio.to_thread(run_feedback_synthesizer, analysis)
            yield event("feedback", "done", result=feedback)

            yield event("persona", "running", message="Building user personas...")
            from agents.persona_builder import run_persona_builder
            personas = await asyncio.to_thread(run_persona_builder, analysis)
            yield event("persona", "done", result=personas)

            from database import save_user_research
            save_user_research(analysis_id, interview, feedback, personas)
            yield event("complete", "done", message="User research complete!")
        except Exception as e:
            yield event("error", "error", message=str(e))

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/prd/{analysis_id}", response_class=HTMLResponse)
async def prd_page(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        return RedirectResponse(url="/login", status_code=302)
    analysis = get_analysis(analysis_id)
    if not analysis:
        return HTMLResponse(content="<h1>Not found</h1>", status_code=404)
    existing_prd = get_prd(analysis_id)
    prd_content = existing_prd["prd"] if existing_prd else ""
    review_content = existing_prd["review"] if existing_prd else ""
    html = "<!DOCTYPE html><html><head><title>PRD Generator</title>" + base_style() + "</head>"
    html += "<body><div class=\"header\"><h1>PRD Generator</h1><a href=\"/logout\" style=\"color:#888;font-size:13px\">Logout</a></div>"
    html += "<div class=\"container\"><a class=\"link\" href=\"/result/" + analysis_id + "\">&larr; Back</a><div style=\"margin-top:24px\">"
    html += "<button class=\"btn\" id=\"genbtn\" onclick=\"generatePRD('" + analysis_id + "')\">Generate PRD with AI</button>"
    html += "<a href=\"/download-prd/" + analysis_id + "\" class=\"btn btn-green\">Download PRD</a>"
    html += "<div id=\"agents\">"
    html += "<div class=\"agent\" id=\"card-prd_writer\"><div class=\"atitle\">1. PRD Writer</div><div class=\"astatus\" id=\"status-prd_writer\">Waiting</div></div>"
    html += "<div class=\"agent\" id=\"card-prd_reviewer\"><div class=\"atitle\">2. Quality Reviewer</div><div class=\"astatus\" id=\"status-prd_reviewer\">Waiting</div></div>"
    html += "</div>"
    html += "<div class=\"card\"><h2>Product Requirements Document</h2><p id=\"prd-content\">" + prd_content + "</p></div>"
    html += "<div class=\"card\"><h2>Quality Review</h2><p id=\"review-content\">" + review_content + "</p></div>"
    html += "</div></div>"
    html += """<script>
async function generatePRD(id) {
    const btn = document.getElementById("genbtn");
    btn.disabled = true; btn.textContent = "Generating...";
    ["prd_writer","prd_reviewer"].forEach(a => {
        document.getElementById("card-"+a).className = "agent";
        document.getElementById("status-"+a).textContent = "Waiting";
        document.getElementById("status-"+a).className = "astatus";
    });
    const res = await fetch("/generate-prd/"+id, {method:"POST"});
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    while(true) {
        const {done, value} = await reader.read();
        if(done) break;
        const lines = dec.decode(value).split("\n").filter(l => l.startsWith("data: "));
        for(const line of lines) {
            try {
                const d = JSON.parse(line.slice(6));
                if(d.agent === "complete") { btn.disabled=false; btn.textContent="Regenerate PRD"; continue; }
                if(d.agent === "error") { btn.disabled=false; btn.textContent="Generate PRD with AI"; alert(d.message); continue; }
                const card = document.getElementById("card-"+d.agent);
                const status = document.getElementById("status-"+d.agent);
                if(d.status === "running") { card.className="agent running"; status.className="astatus running"; status.textContent=d.message; }
                if(d.status === "done" && d.result) {
                    card.className="agent done"; status.className="astatus done"; status.textContent="Complete";
                    if(d.agent === "prd_writer") document.getElementById("prd-content").textContent = d.result;
                    if(d.agent === "prd_reviewer") document.getElementById("review-content").textContent = d.result;
                }
            } catch(e) {}
        }
    }
}
</script></body></html>"""
    return HTMLResponse(content=html)

@app.post("/generate-prd/{analysis_id}")
async def generate_prd(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        async def deny():
            yield event("error", "error", message="Not authenticated.")
        return StreamingResponse(deny(), media_type="text/event-stream")
    analysis = get_analysis(analysis_id)
    if not analysis:
        async def not_found():
            yield event("error", "error", message="Analysis not found.")
        return StreamingResponse(not_found(), media_type="text/event-stream")

    async def generate():
        try:
            yield event("prd_writer", "running", message="Writing PRD document...")
            from agents.prd_writer import run_prd_writer
            prd = await asyncio.to_thread(run_prd_writer, analysis)
            yield event("prd_writer", "done", result=prd)

            yield event("prd_reviewer", "running", message="Reviewing PRD quality...")
            from agents.prd_reviewer import run_prd_reviewer
            review = await asyncio.to_thread(run_prd_reviewer, prd)
            yield event("prd_reviewer", "done", result=review)

            prd_id = save_prd(analysis_id, prd, review)
            filename = "/root/ai-pm-agent/outputs/prd_" + analysis_id + ".txt"
            with open(filename, "w") as f:
                f.write("PRODUCT REQUIREMENTS DOCUMENT\n")
                f.write("=" * 50 + "\n\n")
                f.write(prd)
                f.write("\n\n" + "=" * 50 + "\n")
                f.write("QUALITY REVIEW\n\n")
                f.write(review)

            yield event("complete", "done", id=prd_id, message="PRD complete!")
        except Exception as e:
            yield event("error", "error", message=str(e))

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/download-prd/{analysis_id}")
async def download_prd(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        return RedirectResponse(url="/login", status_code=302)
    existing_prd = get_prd(analysis_id)
    if not existing_prd:
        return HTMLResponse(content="<h1>No PRD found. Generate one first.</h1>", status_code=404)
    content_text = "PRODUCT REQUIREMENTS DOCUMENT\n"
    content_text += "=" * 50 + "\n\n"
    content_text += existing_prd["prd"]
    content_text += "\n\n" + "=" * 50 + "\n"
    content_text += "QUALITY REVIEW\n\n"
    content_text += existing_prd["review"]
    return PlainTextResponse(
        content=content_text,
        headers={"Content-Disposition": "attachment; filename=prd_" + analysis_id + ".txt"}
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(session: str = Cookie(default=None)):
    if not is_authenticated(session):
        return RedirectResponse(url="/login", status_code=302)
    analyses = get_all_analyses()
    from database import get_prd, get_user_research, get_backlog
    cards = ""
    for a in analyses:
        idea = a["raw_idea"][:70] + "..." if len(a["raw_idea"]) > 70 else a["raw_idea"]
        has_research = get_user_research(a["id"]) is not None
        has_prd = get_prd(a["id"]) is not None
        p1_badge = "<span style=\"background:#2a5a3a;color:#4caf7d;padding:4px 10px;border-radius:20px;font-size:12px;margin-right:6px\">Phase 1 ✓</span>"
        p2_badge = "<span style=\"background:#2a5a3a;color:#4caf7d;padding:4px 10px;border-radius:20px;font-size:12px;margin-right:6px\">Phase 2 ✓</span>" if has_research else "<span style=\"background:#2a2a2a;color:#888;padding:4px 10px;border-radius:20px;font-size:12px;margin-right:6px\">Phase 2 —</span>"
        p3_badge = "<span style=\"background:#2a5a3a;color:#4caf7d;padding:4px 10px;border-radius:20px;font-size:12px;margin-right:6px\">Phase 3 ✓</span>" if has_prd else "<span style=\"background:#2a2a2a;color:#888;padding:4px 10px;border-radius:20px;font-size:12px;margin-right:6px\">Phase 3 —</span>"
        has_backlog = get_backlog(a["id"]) is not None
        p5_badge = "<span style=\"background:#1a3a5a;color:#4a9eff;padding:4px 10px;border-radius:20px;font-size:12px;margin-right:6px\">Phase 5 ✓</span>" if has_backlog else "<span style=\"background:#2a2a2a;color:#888;padding:4px 10px;border-radius:20px;font-size:12px;margin-right:6px\">Phase 5 —</span>"
        cards += "<div style=\"background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:24px;margin-bottom:16px\">"
        cards += "<div style=\"font-size:12px;color:#888;margin-bottom:8px\">" + str(a["created_at"])[:16] + "</div>"
        cards += "<div style=\"font-size:16px;color:#e0e0e0;margin-bottom:16px;font-weight:500\">" + idea + "</div>"
        cards += "<div style=\"margin-bottom:16px\">" + p1_badge + p2_badge + p3_badge + p5_badge + "</div>"
        cards += "<div style=\"display:flex;gap:8px;flex-wrap:wrap\">"
        cards += "<a href=\"/result/" + a["id"] + "\" style=\"background:#2a2a4a;color:#7c6fcd;padding:6px 14px;border-radius:6px;font-size:13px;text-decoration:none\">Analysis</a>"
        cards += "<a href=\"/research/" + a["id"] + "\" style=\"background:#2a2a4a;color:#7c6fcd;padding:6px 14px;border-radius:6px;font-size:13px;text-decoration:none\">Research</a>"
        cards += "<a href=\"/prd/" + a["id"] + "\" style=\"background:#2a2a4a;color:#7c6fcd;padding:6px 14px;border-radius:6px;font-size:13px;text-decoration:none\">PRD</a>"
        cards += "<a href=\"/backlog/" + a["id"] + "\" style=\"background:#1a2a3a;color:#4a9eff;padding:6px 14px;border-radius:6px;font-size:13px;text-decoration:none\">Backlog</a>"
        cards += "</div></div>"
    if not cards:
        cards = "<p style=\"color:#888\">No analyses yet. Go back and run one!</p>"
    total = len(analyses)
    complete = sum(1 for a in analyses if get_prd(a["id"]) is not None)
    html = "<!DOCTYPE html><html><head><title>AI PM Dashboard</title>" + base_style() + """
    <style>
    .stat{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:20px;text-align:center;flex:1}
    .stat-num{font-size:36px;font-weight:bold;color:#7c6fcd}
    .stat-label{font-size:13px;color:#888;margin-top:4px}
    </style></head>"""
    html += "<body><div class=\"header\"><h1>AI PM Dashboard</h1><a href=\"/logout\" style=\"color:#888;font-size:13px\">Logout</a></div>"
    html += "<div class=\"container\">"
    html += "<div style=\"display:flex;gap:16px;margin-bottom:32px;margin-top:24px\">"
    html += "<div class=\"stat\"><div class=\"stat-num\">" + str(total) + "</div><div class=\"stat-label\">Total Ideas</div></div>"
    html += "<div class=\"stat\"><div class=\"stat-num\">" + str(complete) + "</div><div class=\"stat-label\">Full PRDs Generated</div></div>"
    html += "<div class=\"stat\"><div class=\"stat-num\">" + str(total * 6) + "</div><div class=\"stat-label\">Agent Runs</div></div>"
    html += "</div>"
    html += "<div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:20px\">"
    html += "<h2 style=\"font-size:18px;color:#e0e0e0;margin:0\">Your Ideas</h2>"
    html += "<a href=\"/\" class=\"btn\">+ New Idea</a>"
    html += "</div>"
    html += cards
    html += "</div></body></html>"
    return HTMLResponse(content=html)


@app.get("/backlog/{analysis_id}", response_class=HTMLResponse)
async def backlog_page(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        return RedirectResponse(url="/login", status_code=302)
    analysis = get_analysis(analysis_id)
    if not analysis:
        return HTMLResponse(content="<h1>Not found</h1>", status_code=404)
    from database import get_backlog
    existing = get_backlog(analysis_id)
    backlog_content = existing["backlog"] if existing else ""
    sprint_content = existing["sprint_plan"] if existing else ""
    html = "<!DOCTYPE html><html><head><title>Backlog Creator</title>" + base_style() + "</head>"
    html += "<body><div class=\"header\"><h1>Backlog Creator</h1><a href=\"/logout\" style=\"color:#888;font-size:13px\">Logout</a></div>"
    html += "<div class=\"container\"><a class=\"link\" href=\"/result/" + analysis_id + "\">&larr; Back</a><div style=\"margin-top:24px\">"
    html += "<button class=\"btn\" id=\"genbtn\" onclick=\"generateBacklog('" + analysis_id + "')\">Generate Backlog with AI</button>"
    html += "<div id=\"agents\">"
    html += "<div class=\"agent\" id=\"card-backlog\"><div class=\"atitle\">1. Backlog Creator</div><div class=\"astatus\" id=\"status-backlog\">Waiting</div></div>"
    html += "<div class=\"agent\" id=\"card-sprint\"><div class=\"atitle\">2. Sprint Planner</div><div class=\"astatus\" id=\"status-sprint\">Waiting</div></div>"
    html += "</div>"
    html += "<div class=\"card\"><h2>Product Backlog</h2><p id=\"backlog-content\">" + backlog_content + "</p></div>"
    html += "<div class=\"card\"><h2>Sprint Plan</h2><p id=\"sprint-content\">" + sprint_content + "</p></div>"
    html += "</div></div>"
    html += """<script>
async function generateBacklog(id) {
    const btn = document.getElementById("genbtn");
    btn.disabled = true; btn.textContent = "Generating...";
    ["backlog","sprint"].forEach(a => {
        document.getElementById("card-"+a).className = "agent";
        document.getElementById("status-"+a).textContent = "Waiting";
        document.getElementById("status-"+a).className = "astatus";
    });
    const res = await fetch("/generate-backlog/"+id, {method:"POST"});
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    while(true) {
        const {done, value} = await reader.read();
        if(done) break;
        const lines = dec.decode(value).split("\n").filter(l => l.startsWith("data: "));
        for(const line of lines) {
            try {
                const d = JSON.parse(line.slice(6));
                if(d.agent === "complete") { btn.disabled=false; btn.textContent="Regenerate Backlog"; continue; }
                if(d.agent === "error") { btn.disabled=false; btn.textContent="Generate Backlog with AI"; alert(d.message); continue; }
                const card = document.getElementById("card-"+d.agent);
                const status = document.getElementById("status-"+d.agent);
                if(d.status === "running") { card.className="agent running"; status.className="astatus running"; status.textContent=d.message; }
                if(d.status === "done" && d.result) {
                    card.className="agent done"; status.className="astatus done"; status.textContent="Complete";
                    if(d.agent === "backlog") document.getElementById("backlog-content").textContent = d.result;
                    if(d.agent === "sprint") document.getElementById("sprint-content").textContent = d.result;
                }
            } catch(e) {}
        }
    }
}
</script></body></html>"""
    return HTMLResponse(content=html)

@app.post("/generate-backlog/{analysis_id}")
async def generate_backlog(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        async def deny():
            yield event("error", "error", message="Not authenticated.")
        return StreamingResponse(deny(), media_type="text/event-stream")
    analysis = get_analysis(analysis_id)
    if not analysis:
        async def not_found():
            yield event("error", "error", message="Analysis not found.")
        return StreamingResponse(not_found(), media_type="text/event-stream")
    from database import get_prd
    existing_prd = get_prd(analysis_id)
    prd_text = existing_prd["prd"] if existing_prd else str(analysis.get("refined_problem","")) + " " + str(analysis.get("validation",""))

    async def generate():
        try:
            yield event("backlog", "running", message="Creating product backlog...")
            from agents.backlog_creator import run_backlog_creator
            backlog = await asyncio.to_thread(run_backlog_creator, prd_text)
            yield event("backlog", "done", result=backlog)

            yield event("sprint", "running", message="Planning sprints...")
            from agents.sprint_planner import run_sprint_planner
            sprint_plan = await asyncio.to_thread(run_sprint_planner, backlog)
            yield event("sprint", "done", result=sprint_plan)

            from database import save_backlog
            save_backlog(analysis_id, backlog, sprint_plan)
            yield event("complete", "done", message="Backlog complete!")
        except Exception as e:
            yield event("error", "error", message=str(e))

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/specs/{analysis_id}", response_class=HTMLResponse)
async def specs_page(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        return RedirectResponse(url="/login", status_code=302)
    analysis = get_analysis(analysis_id)
    if not analysis:
        return HTMLResponse(content="<h1>Not found</h1>", status_code=404)
    from database import get_specs, get_backlog
    existing = get_specs(analysis_id)
    existing_backlog = get_backlog(analysis_id)
    design = existing["design_brief"] if existing else ""
    backend = existing["backend_spec"] if existing else ""
    frontend = existing["frontend_spec"] if existing else ""
    has_backlog = existing_backlog is not None
    warning = "" if has_backlog else "<div style=\"background:#3a2a1a;border:1px solid #5a3a1a;border-radius:8px;padding:12px;margin-bottom:20px;color:#ffaa44;font-size:14px\">Generate a backlog first for best results. <a href=\"/backlog/" + analysis_id + "\" style=\"color:#ffaa44\">Create Backlog</a></div>"
    backlog_text = existing_backlog["backlog"] if existing_backlog else ""
    html = "<!DOCTYPE html><html><head><title>Specs</title>" + base_style() + "</head>"
    html += "<body><div class=\"header\"><h1>Parallel Spec Generator</h1><a href=\"/logout\" style=\"color:#888;font-size:13px\">Logout</a></div>"
    html += "<div class=\"container\"><a class=\"link\" href=\"/backlog/" + analysis_id + "\">&larr; Back to Backlog</a><div style=\"margin-top:24px\">"
    html += warning
    html += "<div style=\"background:#1a2a3a;border:1px solid #2a3a5a;border-radius:10px;padding:16px;margin-bottom:20px\">"
    html += "<p style=\"color:#4a9eff;font-size:14px;margin:0\">Design Agent + Backend Agent run in parallel. Frontend Agent starts after Design completes.</p>"
    html += "</div>"
    html += "<button class=\"btn\" id=\"genbtn\" onclick=\"generateSpecs('" + analysis_id + "')\">Run Parallel Agents</button>"
    html += "<div id=\"agents\" style=\"display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px\">"
    html += "<div class=\"agent\" id=\"card-design\"><div class=\"atitle\">Design Agent</div><div style=\"font-size:11px;color:#ffaa44;margin-bottom:4px\">Runs in parallel</div><div class=\"astatus\" id=\"status-design\">Waiting</div></div>"
    html += "<div class=\"agent\" id=\"card-backend\"><div class=\"atitle\">Backend Agent</div><div style=\"font-size:11px;color:#ffaa44;margin-bottom:4px\">Runs in parallel</div><div class=\"astatus\" id=\"status-backend\">Waiting</div></div>"
    html += "</div>"
    html += "<div class=\"agent\" id=\"card-frontend\" style=\"margin-bottom:20px\"><div class=\"atitle\">Frontend Agent</div><div style=\"font-size:11px;color:#888;margin-bottom:4px\">Starts after Design completes</div><div class=\"astatus\" id=\"status-frontend\">Waiting for Design</div></div>"
    html += "<div class=\"card\"><h2>Design Brief</h2><p id=\"design-content\">" + design + "</p></div>"
    html += "<div class=\"card\"><h2>Backend Spec</h2><p id=\"backend-content\">" + backend + "</p></div>"
    html += "<div class=\"card\"><h2>Frontend Spec</h2><p id=\"frontend-content\">" + frontend + "</p></div>"
    html += "</div></div>"
    html += """<script>
async function generateSpecs(id) {
    const btn = document.getElementById("genbtn");
    btn.disabled = true; btn.textContent = "Running parallel agents...";
    ["design","backend","frontend"].forEach(a => {
        document.getElementById("card-"+a).className = "agent";
        document.getElementById("status-"+a).textContent = "Waiting";
        document.getElementById("status-"+a).className = "astatus";
    });
    const res = await fetch("/generate-specs/"+id, {method:"POST"});
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    while(true) {
        const {done, value} = await reader.read();
        if(done) break;
        const lines = dec.decode(value).split("\n").filter(l => l.startsWith("data: "));
        for(const line of lines) {
            try {
                const d = JSON.parse(line.slice(6));
                if(d.agent === "complete") { btn.disabled=false; btn.textContent="Re-run Agents"; continue; }
                if(d.agent === "error") { btn.disabled=false; btn.textContent="Run Parallel Agents"; alert(d.message); continue; }
                const card = document.getElementById("card-"+d.agent);
                const status = document.getElementById("status-"+d.agent);
                if(d.status === "running") { card.className="agent running"; status.className="astatus running"; status.textContent=d.message; }
                if(d.status === "done" && d.result) {
                    card.className="agent done"; status.className="astatus done"; status.textContent="Complete";
                    if(d.agent === "design") document.getElementById("design-content").textContent = d.result;
                    if(d.agent === "backend") document.getElementById("backend-content").textContent = d.result;
                    if(d.agent === "frontend") document.getElementById("frontend-content").textContent = d.result;
                }
            } catch(e) {}
        }
    }
}
</script></body></html>"""
    return HTMLResponse(content=html)

@app.post("/generate-specs/{analysis_id}")
async def generate_specs(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        async def deny():
            yield event("error", "error", message="Not authenticated.")
        return StreamingResponse(deny(), media_type="text/event-stream")
    analysis = get_analysis(analysis_id)
    if not analysis:
        async def not_found():
            yield event("error", "error", message="Analysis not found.")
        return StreamingResponse(not_found(), media_type="text/event-stream")
    from database import get_backlog
    existing_backlog = get_backlog(analysis_id)
    backlog_text = existing_backlog["backlog"] if existing_backlog else str(analysis.get("refined_problem",""))

    async def generate():
        try:
            yield event("design", "running", message="Creating design brief...")
            yield event("backend", "running", message="Writing backend spec...")

            from agents.design_agent import run_design_agent
            from agents.backend_agent import run_backend_agent

            design, backend = await asyncio.gather(
                asyncio.to_thread(run_design_agent, backlog_text),
                asyncio.to_thread(run_backend_agent, backlog_text)
            )

            yield event("design", "done", result=design)
            yield event("backend", "done", result=backend)

            yield event("frontend", "running", message="Building frontend spec (using design output)...")
            from agents.frontend_agent import run_frontend_agent
            frontend = await asyncio.to_thread(run_frontend_agent, backlog_text, design)
            yield event("frontend", "done", result=frontend)

            from database import save_specs
            save_specs(analysis_id, design, backend, frontend)
            yield event("complete", "done", message="All specs complete!")
        except Exception as e:
            yield event("error", "error", message=str(e))

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/architecture/{analysis_id}", response_class=HTMLResponse)
async def architecture_page(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        return RedirectResponse(url="/login", status_code=302)
    analysis = get_analysis(analysis_id)
    if not analysis:
        return HTMLResponse(content="<h1>Not found</h1>", status_code=404)
    from database import get_architecture
    existing = get_architecture(analysis_id)
    arch = existing["architecture"] if existing else ""
    qa = existing["qa_plan"] if existing else ""
    devops = existing["devops_plan"] if existing else ""
    html = "<!DOCTYPE html><html><head><title>Architecture</title>" + base_style() + "</head>"
    html += "<body><div class=\"header\"><h1>System Architecture</h1><a href=\"/logout\" style=\"color:#888;font-size:13px\">Logout</a></div>"
    html += "<div class=\"container\"><a class=\"link\" href=\"/result/" + analysis_id + "\">&larr; Back</a><div style=\"margin-top:24px\">"
    html += "<div style=\"background:#1a2a3a;border:1px solid #2a3a5a;border-radius:10px;padding:16px;margin-bottom:20px\">"
    html += "<p style=\"color:#4a9eff;font-size:14px;margin:0\">Architect runs first. QA + DevOps run in parallel after.</p></div>"
    html += "<button class=\"btn\" id=\"genbtn\" onclick=\"generateArchitecture('" + analysis_id + "')\">Run Architecture Agents</button>"
    html += "<div id=\"agents\">"
    html += "<div class=\"agent\" id=\"card-architect\"><div class=\"atitle\">1. Solutions Architect</div><div class=\"astatus\" id=\"status-architect\">Waiting</div></div>"
    html += "<div style=\"display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px\">"
    html += "<div class=\"agent\" id=\"card-qa\"><div class=\"atitle\">2. QA Engineer</div><div style=\"font-size:11px;color:#ffaa44\">Runs in parallel</div><div class=\"astatus\" id=\"status-qa\">Waiting</div></div>"
    html += "<div class=\"agent\" id=\"card-devops\"><div class=\"atitle\">3. DevOps Engineer</div><div style=\"font-size:11px;color:#ffaa44\">Runs in parallel</div><div class=\"astatus\" id=\"status-devops\">Waiting</div></div>"
    html += "</div></div>"
    html += "<div class=\"card\"><h2>System Architecture</h2><p id=\"arch-content\">" + arch + "</p></div>"
    html += "<div style=\"display:grid;grid-template-columns:1fr 1fr;gap:16px\">"
    html += "<div class=\"card\"><h2>QA Test Plan</h2><p id=\"qa-content\">" + qa + "</p></div>"
    html += "<div class=\"card\"><h2>DevOps Setup</h2><p id=\"devops-content\">" + devops + "</p></div>"
    html += "</div></div></div>"
    html += """<script>
async function generateArchitecture(id) {
    const btn = document.getElementById("genbtn");
    btn.disabled = true; btn.textContent = "Running agents...";
    ["architect","qa","devops"].forEach(a => {
        document.getElementById("card-"+a).className = "agent";
        document.getElementById("status-"+a).textContent = "Waiting";
        document.getElementById("status-"+a).className = "astatus";
    });
    const res = await fetch("/generate-architecture/"+id, {method:"POST"});
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    while(true) {
        const {done, value} = await reader.read();
        if(done) break;
        const lines = dec.decode(value).split("\n").filter(l => l.startsWith("data: "));
        for(const line of lines) {
            try {
                const d = JSON.parse(line.slice(6));
                if(d.agent === "complete") { btn.disabled=false; btn.textContent="Re-run Agents"; continue; }
                if(d.agent === "error") { btn.disabled=false; btn.textContent="Run Architecture Agents"; alert(d.message); continue; }
                const card = document.getElementById("card-"+d.agent);
                const status = document.getElementById("status-"+d.agent);
                if(d.status === "running") { card.className="agent running"; status.className="astatus running"; status.textContent=d.message; }
                if(d.status === "done" && d.result) {
                    card.className="agent done"; status.className="astatus done"; status.textContent="Complete";
                    if(d.agent === "architect") document.getElementById("arch-content").textContent = d.result;
                    if(d.agent === "qa") document.getElementById("qa-content").textContent = d.result;
                    if(d.agent === "devops") document.getElementById("devops-content").textContent = d.result;
                }
            } catch(e) {}
        }
    }
}
</script></body></html>"""
    return HTMLResponse(content=html)

@app.post("/generate-architecture/{analysis_id}")
async def generate_architecture(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        async def deny():
            yield event("error", "error", message="Not authenticated.")
        return StreamingResponse(deny(), media_type="text/event-stream")
    analysis = get_analysis(analysis_id)
    if not analysis:
        async def not_found():
            yield event("error", "error", message="Analysis not found.")
        return StreamingResponse(not_found(), media_type="text/event-stream")
    from database import get_specs, get_prd, get_backlog
    specs = get_specs(analysis_id) or {}
    prd_data = get_prd(analysis_id) or {}
    backlog_data = get_backlog(analysis_id) or {}
    prd_text = prd_data.get("prd", str(analysis.get("refined_problem","")))
    backlog_text = backlog_data.get("backlog", "")

    async def generate():
        try:
            yield event("architect", "running", message="Designing system architecture...")
            from agents.architect_agent import run_architect_agent
            architecture = await asyncio.to_thread(run_architect_agent, specs)
            yield event("architect", "done", result=architecture)

            yield event("qa", "running", message="Writing QA test plan...")
            yield event("devops", "running", message="Setting up DevOps pipeline...")

            from agents.qa_agent import run_qa_agent
            from agents.devops_agent import run_devops_agent

            qa_plan, devops_plan = await asyncio.gather(
                asyncio.to_thread(run_qa_agent, prd_text, backlog_text),
                asyncio.to_thread(run_devops_agent, architecture)
            )

            yield event("qa", "done", result=qa_plan)
            yield event("devops", "done", result=devops_plan)

            from database import save_architecture
            save_architecture(analysis_id, architecture, qa_plan, devops_plan)
            yield event("complete", "done", message="Architecture complete!")
        except Exception as e:
            yield event("error", "error", message=str(e))

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/analyse")
async def analyse(request: Request, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        async def deny():
            yield event("error", "error", message="Not authenticated. Please login.")
        return StreamingResponse(deny(), media_type="text/event-stream")
    data = await request.json()
    raw_idea = data.get("idea", "")

    async def generate():
        try:
            yield event("idea_refiner", "running", message="Refining your idea...")
            refined = await asyncio.to_thread(run_idea_refiner, raw_idea)
            yield event("idea_refiner", "done", result=refined)

            yield event("market_researcher", "running", message="Researching market...")
            market = await asyncio.to_thread(run_market_researcher, refined)
            yield event("market_researcher", "done", result=market)

            yield event("user_identifier", "running", message="Finding real users...")
            users = await asyncio.to_thread(run_user_identifier, refined)
            yield event("user_identifier", "done", result=users)

            yield event("validator", "running", message="Validating idea...")
            combined = "MARKET:\n" + market + "\n\nUSERS:\n" + users
            validation = await asyncio.to_thread(run_validator, refined, combined)
            yield event("validator", "done", result=validation)

            analysis_id = save_analysis(raw_idea, refined, market, users, validation)
            yield event("complete", "done", id=analysis_id, message="Done!")
        except Exception as e:
            yield event("error", "error", message=str(e))

    return StreamingResponse(generate(), media_type="text/event-stream")
