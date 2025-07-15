# This file
from fastapi import APIRouter, Query, UploadFile, File, HTTPException, Body
from pydantic import BaseModel
from typing import List
import os
import pdfplumber
import json
from utils import resume_parser
from utils.question_generator import generate_questions_from_resume
from routes.video_interview import run_video_interview
from utils.voice_assistant import speak_question
from fastapi import APIRouter, Query
from utils.gemini_api import generate_interview_questions, get_feedback
from datetime import datetime


router = APIRouter()
class InterviewLog(BaseModel):
    candidate_name: str
    responses: list  # list of { "question": ..., "answer": ... }

@router.post("/interview/log")
async def save_interview_log(log: InterviewLog):
    try:
        log_data = {
            "candidate_name": log.candidate_name,
            "responses": log.responses,
            "submitted_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gemini/questions")
def gemini_questions(job_title: str, language: str = 'en'):
    questions = generate_interview_questions(job_title, language)
    return {"questions": questions}

@router.get("/gemini/feedback")
def gemini_feedback(answer: str, language: str = 'en'):
    feedback = get_feedback(answer, language)
    return {"feedback": feedback}

# Global dictionary to store parsed resume data
parsed_resume_data = {}

# ✅ Pydantic models
class QAItem(BaseModel):
    question: str
    answer: str

class InterviewLog(BaseModel):
    candidate_name: str
    responses: List[QAItem]

def get_questions_for_job(job_title: str, language: str = "en"):
    if language == "ur":
        return [
            f"{job_title} کے لیے کون سی مہارتیں اہم ہیں؟",
            f"اپنے {job_title} کے تجربے کے بارے میں بتائیں۔",
            f"آپ اس {job_title} پوزیشن میں کیوں دلچسپی رکھتے ہیں؟"
        ]
    else:
        return [
            f"What skills are important for a {job_title}?",
            f"Describe your experience relevant to {job_title}.",
            f"Why are you interested in the {job_title} position?"
        ]

@router.get("/interview/questions")
async def fetch_questions_for_job(
    job_title: str = Query(..., description="Job title to fetch questions for"),
    language: str = Query("en", description="Language for questions"),
    experience_level: str = Query("mid", description="Experience level"),
    count: int = Query(10, description="Number of questions")
):
    # Generate questions using all parameters
    questions = generate_questions_from_resume(
        job_title=job_title,
        language=language,
        experience_level=experience_level,
        count=count
    )
    return {
        "job": job_title,
        "questions": questions
    }

@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    os.makedirs("temp_files", exist_ok=True)
    temp_path = f"temp_files/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    extracted_text = ""
    with pdfplumber.open(temp_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"

    os.remove(temp_path)

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in the PDF.")

    parsed_resume_data["text"] = extracted_text.strip()
    return {"resume_text": extracted_text.strip()}

@router.get("/questions/generate")
def generate_interview_questions():
    if not parsed_resume_data.get("text"):
        raise HTTPException(status_code=400, detail="No resume data found.")
    questions = generate_questions_from_resume(parsed_resume_data["text"])
    return {"questions": questions}

@router.post("/speak")
async def speak_question_api(question: str = Body(...), language: str = Body("en")):
    try:
        speak_question(question, language)
        return {"status": "spoken"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Speech failed")

@router.post("/interview/start")
async def start_interview_with_resume(file: UploadFile = File(...)):
    try:
        print("[INFO] Received file:", file.filename)

        os.makedirs("temp_files", exist_ok=True)
        temp_path = f"temp_files/{file.filename}"

        # Save the uploaded file
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        print("[INFO] Saved temp resume at:", temp_path)

        # ✅ Ensure resume_parser works and returns text
        resume_data = resume_parser.parse_resume(temp_path)
        if not resume_data or not resume_data.get("text"):
            print("[ERROR] No text extracted from resume.")
            raise HTTPException(status_code=400, detail="Resume parsing failed. No text extracted.")

        # Extract text using the new utility function
        ext = temp_path.lower().split('.')[-1]
        if ext == "pdf":
            resume_text = resume_parser.extract_text_from_pdf(temp_path)
        elif ext == "docx":
            resume_text = resume_parser.extract_text_from_docx(temp_path)
        elif ext in ["jpg", "jpeg", "png"]:
            resume_text = resume_parser.extract_text_from_image(temp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        if not resume_text or not resume_text.strip():
            print("[ERROR] No text extracted from resume.")
            raise HTTPException(status_code=400, detail="Resume parsing failed. No text extracted.")

        print("[INFO] Resume text extracted successfully.")

        # Detect language of the resume
        lang = resume_parser.detect_language(resume_text)
        print(f"[INFO] Resume language detected: {lang}")

        # ✅ Generate interview questions
        questions = generate_questions_from_resume(resume_text, lang=lang)
        
        # Run video interview with error handling
        try:
            run_video_interview(questions)
        except Exception as inner_error:
            print(f"[ERROR] run_video_interview failed: {inner_error}")
            raise HTTPException(status_code=500, detail="Video interview could not be started. Check your webcam/audio setup.")

        return {"message": "Interview started"}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"[ERROR] Interview start failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to start interview due to server error.")

@router.post("/interview/log")
async def save_interview_log_route(log: InterviewLog):
    try:
        save_interview_log(log.dict())
        return {"message": "Log saved successfully."}
    except Exception as e:
        print(f"[ERROR] Failed to save log: {e}")
        raise HTTPException(status_code=500, detail="Failed to save log.")

# ✅ Add this endpoint for submitting logs (compatible with your prompt)
@router.post("/interview/submit_log")
async def submit_log(log: InterviewLog):
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/interview_logs.json", "a", encoding="utf-8") as f:
            json.dump(log.dict(), f, ensure_ascii=False)
            f.write(",\n")
        return {"message": "Log submitted successfully"}
    except Exception as e:
        print(f"[ERROR] Failed to save log: {e}")
        raise HTTPException(status_code=500, detail="Failed to save log.")

@router.get("/interview/logs")
async def get_all_logs():
    log_file = "logs/interview_logs.json"
    if not os.path.exists(log_file):
        return []
    with open(log_file, "r", encoding="utf-8") as f:
        return json.load(f)

import os
import json

def save_interview_log(log_data, log_file="logs/interview_logs.json"):
    os.makedirs("logs", exist_ok=True)
    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except Exception:
                logs = []
    logs.append(log_data)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
