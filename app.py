from fastapi import FastAPI, Request, Cookie
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
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

LOGIN_ERROR_HTML = LOGIN_HTML.replace(
    "<div class=\"error\"></div>",
    "<div class=\"error\">Incorrect password.</div>"
)

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
        rows += "<a href=\"/result/" + a["id"] + "\" style=\"background:#7c6fcd;color:white;padding:6px 14px;border-radius:6px;font-size:13px;text-decoration:none\">View Analysis</a>"
        rows += "</div>"
    if not rows:
        rows = "<p style=\"color:#888\">No analyses yet.</p>"
    html = """<!DOCTYPE html><html><head><title>History</title>
    <style>body{font-family:sans-serif;background:#0f0f0f;color:#e0e0e0;margin:0}
    .header{background:#1a1a2e;padding:24px 40px;display:flex;align-items:center;justify-content:space-between}
    .header h1{color:#7c6fcd;font-size:24px;margin:0}
    .container{max-width:900px;margin:40px auto;padding:0 20px}
    a{color:#7c6fcd;text-decoration:none;font-size:14px}</style></head>
    <body><div class="header"><h1>Analysis History</h1>
    <a href="/logout" style="color:#888;font-size:13px">Logout</a></div>
    <div class="container"><a href="/">&larr; Back</a>
    <div style="margin-top:24px">""" + rows + """</div></div></body></html>"""
    return HTMLResponse(content=html)

@app.get("/result/{analysis_id}", response_class=HTMLResponse)
async def result(analysis_id: str, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        return RedirectResponse(url="/login", status_code=302)
    data = get_analysis(analysis_id)
    if not data:
        return HTMLResponse(content="<h1>Not found</h1>", status_code=404)
    def section(title, content):
        return "<div style=\"background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:24px;margin-bottom:20px\"><h2 style=\"color:#7c6fcd;font-size:16px;margin:0 0 12px\">" + title + "</h2><p style=\"font-size:14px;color:#ccc;line-height:1.7;white-space:pre-wrap;margin:0\">" + str(content) + "</p></div>"
    html = """<!DOCTYPE html><html><head><title>Result</title>
    <style>body{font-family:sans-serif;background:#0f0f0f;color:#e0e0e0;margin:0}
    .header{background:#1a1a2e;padding:24px 40px;display:flex;align-items:center;justify-content:space-between}
    .header h1{color:#7c6fcd;font-size:24px;margin:0}
    .container{max-width:900px;margin:40px auto;padding:0 20px}
    a{color:#7c6fcd;text-decoration:none;font-size:14px}
    .prd-btn{background:#7c6fcd;color:white;padding:12px 28px;border-radius:8px;font-size:15px;text-decoration:none;display:inline-block;margin-top:24px}
    </style></head>
    <body><div class="header"><h1>Analysis Result</h1>
    <a href="/logout" style="color:#888;font-size:13px">Logout</a></div>
    <div class="container"><a href="/history">&larr; History</a>
    <div style="margin-top:24px">"""
    html += section("Raw Idea", data["raw_idea"])
    html += section("Refined Problem", data["refined_problem"])
    html += section("Market Research", data["market_research"])
    html += section("User Profile", data["user_profile"])
    html += section("Validation", data["validation"])
    html += "<a href=\"/prd/" + analysis_id + "\" class=\"prd-btn\">Generate PRD from this analysis</a>"
    html += "</div></div></body></html>"
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
    html = """<!DOCTYPE html><html><head><title>PRD Generator</title>
    <style>body{font-family:sans-serif;background:#0f0f0f;color:#e0e0e0;margin:0}
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
    button{background:#7c6fcd;color:white;border:none;padding:12px 28px;border-radius:8px;font-size:15px;cursor:pointer;margin-bottom:24px}
    button:disabled{background:#444;cursor:not-allowed}
    a{color:#7c6fcd;text-decoration:none;font-size:14px}</style></head>
    <body><div class="header"><h1>PRD Generator</h1>
    <a href="/logout" style="color:#888;font-size:13px">Logout</a></div>
    <div class="container">
    <a href="/result/""" + analysis_id + """">&larr; Back to analysis</a>
    <div style="margin-top:24px">
    <button id="genbtn" onclick="generatePRD('""" + analysis_id + """')">Generate PRD with AI</button>
    <div id="agents">
    <div class="agent" id="card-prd_writer"><div class="atitle">1. PRD Writer</div><div class="astatus" id="status-prd_writer">Waiting</div></div>
    <div class="agent" id="card-prd_reviewer"><div class="atitle">2. Quality Reviewer</div><div class="astatus" id="status-prd_reviewer">Waiting</div></div>
    </div>
    <div class="card" id="prd-card"><h2>Product Requirements Document</h2><p id="prd-content">""" + prd_content + """</p></div>
    <div class="card" id="review-card"><h2>Quality Review</h2><p id="review-content">""" + review_content + """</p></div>
    </div></div>
    <script>
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
    </script>
    </body></html>"""
    return HTMLResponse(content=html)

@app.post("/analyse")
async def analyse(request: Request, session: str = Cookie(default=None)):
    if not is_authenticated(session):
        async def deny():
            yield event("error", "error", message="Not authenticated. Please login.")
        return StreamingResponse(deny(), media_type="text/event-stream")
    data = await request.json()
    raw_idea = data.get("idea", "")
    results = {}

    async def generate():
        try:
            yield event("idea_refiner", "running", message="Refining your idea...")
            refined = await asyncio.to_thread(run_idea_refiner, raw_idea)
            results["refined"] = refined
            yield event("idea_refiner", "done", result=refined)

            yield event("market_researcher", "running", message="Researching market...")
            market = await asyncio.to_thread(run_market_researcher, refined)
            results["market"] = market
            yield event("market_researcher", "done", result=market)

            yield event("user_identifier", "running", message="Finding real users...")
            users = await asyncio.to_thread(run_user_identifier, refined)
            results["users"] = users
            yield event("user_identifier", "done", result=users)

            yield event("validator", "running", message="Validating idea...")
            combined = "MARKET:\n" + market + "\n\nUSERS:\n" + users
            validation = await asyncio.to_thread(run_validator, refined, combined)
            results["validation"] = validation
            yield event("validator", "done", result=validation)

            analysis_id = save_analysis(raw_idea, refined, market, users, validation)
            yield event("complete", "done", id=analysis_id, message="Done!")

        except Exception as e:
            yield event("error", "error", message=str(e))

    return StreamingResponse(generate(), media_type="text/event-stream")
