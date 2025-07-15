from fastapi import FastAPI, Request, Form, Response, status, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from routes.resume import router as resume_router
from routes.interview import router as interview_router
from routes.video_emotion import router as video_emotion_router
from routes.video_interview import router as video_router
from routes import feedback
from routes.admin import router as admin_router
from routes import contact
from routes import admin_logs
from routes.voice import router as voice_router
import fitz  # PyMuPDF
import uuid
import os
import csv
from io import StringIO
import shutil
# Above all the routes import from other files Here link bcz its my backend file 
from utils.auth import verify_login
from utils.resume_parser import extract_text_from_pdf, parse_resume
from utils.gemini_utils import generate_questions_with_gemini

# Create DB tables after import
router = APIRouter()


app = FastAPI(title="Smart Interview Bot")
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

# Enable CORS for frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend domain, e.g., ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/resume", response_class=HTMLResponse)
async def resume(request: Request):
    return templates.TemplateResponse("resume.html", {"request": request})

@app.get("/questions", response_class=HTMLResponse)
async def questions(request: Request):
    return templates.TemplateResponse("questions.html", {"request": request})

@app.get("/emotion", response_class=HTMLResponse)
async def emotion(request: Request):
    return templates.TemplateResponse("emotion.html", {"request": request})

# Register your routes
app.include_router(resume_router, prefix="/resume", tags=["Resume"])
app.include_router(interview_router, prefix="/interview", tags=["Interview"])
app.include_router(video_emotion_router, prefix="/emotion")
app.include_router(video_router)
app.include_router(feedback.router)
app.include_router(admin_router)
app.include_router(contact.router)
app.include_router(voice_router, prefix="/voice")
app.include_router(admin_logs.router)

# ---------------------------------------
# Declare router and define its endpoints
# ---------------------------------------



def extract_text(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        raise
    return text

@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        os.makedirs("uploads", exist_ok=True)
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": "Resume uploaded successfully."}
    except Exception as e:
        print(f"[ERROR] Resume upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload resume.")

def generate_questions(job_title: str):
    if not job_title:
        raise ValueError("Job title is empty")
    job_questions = {
        "Data Analyst": [
            "What is your experience with SQL?",
            "How do you handle missing data in a dataset?",
            "Explain the difference between inner and outer join in SQL."
        ],
        "AI/ML Engineer": [
            "Explain the difference between supervised and unsupervised learning.",
            "What are some common challenges in training deep learning models?"
        ],
        "Frontend Developer": [
            "What is the Virtual DOM in React?",
            "How do you ensure your website is responsive?"
        ]
        # Add more job roles and questions as needed
    }
    return job_questions.get(job_title, ["Generic question 1", "Generic question 2"])

@router.get("/interview/interview/questions")
def get_questions(job_title: str):
    try:
        questions = generate_questions(job_title)
        return {"questions": questions}
    except Exception as e:
        print(f"Question generation error: {e}")
        raise HTTPException(status_code=500, detail="Could not generate questions")

# Routes to serve HTML pages
@app.get("/", response_class=FileResponse)
async def serve_index():
    return "static/index.html"

@app.get("/resume.html", response_class=FileResponse)
async def serve_resume():
    return "static/resume.html"

@app.get("/questions.html", response_class=FileResponse)
async def serve_questions():
    return "static/questions.html"

@app.get("/emotion.html", response_class=FileResponse)
async def serve_emotion():
    return "static/emotion.html"

# Admin Login Page
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_form(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})

# Login POST Handler
@app.post("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if verify_login(username, password):
        request.session["is_admin"] = True
        return RedirectResponse("/admin", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("admin_login.html", {
        "request": request, "error": "Invalid credentials"
    })

# Logout
@app.get("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=status.HTTP_302_FOUND)

# Protect Admin Route
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    # Dummy chart values (replace with DB queries as needed)
    resume_counts = {"uploaded": 15, "not_uploaded": 5}
    interview_counts = {"taken": 10, "pending": 10}
    emotion_counts = {
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "values": [3, 4, 5, 2, 6]
    }

    users = [
        {"name": "Ali", "email": "ali@example.com", "resume": "Yes", "interview": "Yes", "last_active": "2025-06-13"},
        {"name": "Sara", "email": "sara@example.com", "resume": "No", "interview": "No", "last_active": "2025-06-12"},
        # Add more dummy users if needed
    ]

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "users": users,
        "resume_counts": resume_counts,
        "interview_counts": interview_counts,
        "emotion_counts": emotion_counts
    })

@router.get("/admin/download-csv")
def download_csv():
    data = [
        {"Name": "Ali", "Email": "ali@example.com", "Resume": "Yes", "Interview": "Yes", "Last Active": "2025-06-13"},
        {"Name": "Sara", "Email": "sara@example.com", "Resume": "No", "Interview": "No", "Last Active": "2025-06-12"},
        # Add more data as needed
    ]

    def generate_csv():
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        output.seek(0)
        return output

    return StreamingResponse(generate_csv(), media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=admin_data.csv"
    })

@router.get("/questions")
async def get_questions(job_title: str):
    questions = generate_questions_with_gemini(job_title)
    return {"questions": questions}

# Register the local APIRouter for extra endpoints at the bottom
app.include_router(router)

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@router.get("/admin/login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Define admin credentials (replace with secure method in production)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

@router.post("/admin/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
        response.set_cookie(key="admin_logged_in", value="true")
        return response
    return RedirectResponse(url="/admin/login", status_code=302)

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    if request.cookies.get("admin_logged_in") != "true":
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/admin/logout")
async def logout():
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("admin_logged_in")
    return response

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

from fastapi import APIRouter, UploadFile, File
import os

router = APIRouter()

UPLOAD_DIR = "temp_files"  # Make sure this folder exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        if file.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_location)
        else:
            return {"error": "Only PDF files supported currently."}

        parsed = parse_resume(resume_text)
        return {
            "message": "Resume parsed successfully.",
            "data": parsed
        }

    except Exception as e:
        return {"error": str(e)}

from routes import resume  # if file is routes/resume.py

app.include_router(resume.router)
from routes import interview

app.include_router(interview.router)
@app.get("/live", response_class=HTMLResponse)
async def live_interview_page(request: Request):
    return templates.TemplateResponse("live_interview.html", {"request": request})
