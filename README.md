# Ezitech-smart-interview_Bot
# Smart Interview Bot

Smart Interview Bot is an AI-powered web platform to help candidates prepare for interviews with features like resume analysis, AI-generated interview questions, live video interviews with emotion detection, and instant feedback.

## Features

- **Resume Analysis:** Upload your resume (PDF/DOCX) and get AI-generated interview questions tailored to your profile.
- **AI Interview Questions:** Generate questions based on job title, experience level, and language (English/Urdu).
- **Live Video Interview:** Practice interviews in a simulated environment with real-time emotion detection.
- **Speech-to-Text & Text-to-Speech:** Answer questions by speaking or listen to questions read aloud.
- **AI Feedback:** Get instant feedback on your answers using Gemini AI.
- **Admin Dashboard:** Manage users, view logs, and download data.
- **Modern UI:** Responsive, attractive interface using Bootstrap and Tailwind CSS.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Frontend:** HTML, Bootstrap, Tailwind CSS, JavaScript
- **AI/ML:** Gemini API, PyMuPDF, pdfplumber, pytesseract, langdetect
- **Database:** (Optional) SQLite or your preferred DB for user/admin data
- **Other:** OpenCV, SpeechRecognition, pdf2image

## Project Structure

```
smart_interview_bot/
│
├── main.py                  # FastAPI app entry point
├── requirements.txt         # Python dependencies
├── templates/               # Jinja2 HTML templates
│   ├── index.html
│   ├── live_interview.html
│   ├── questions.html
│   └── ...
├── static/                  # Static files (CSS, JS, images)
├── routes/                  # FastAPI route modules
│   ├── resume.py
│   ├── interview.py
│   ├── admin.py
│   └── ...
├── utils/                   # Utility modules (PDF parsing, AI, etc.)
│   ├── resume_parser.py
│   ├── gemini_utils.py
│   └── ...
├── data/                    # Data files (logs, etc.)
│   └── interview_log.json
└── ...
```

## Setup Instructions

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/smart_interview_bot.git
    cd smart_interview_bot
    ```

2. **Create a virtual environment and activate it:**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Install Tesseract OCR and Poppler (for PDF/image parsing):**
    - [Tesseract Download](https://github.com/tesseract-ocr/tesseract)
    - [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/)

5. **Run the application:**
    ```bash
    uvicorn main:app --reload
    ```

6. **Open your browser and visit:**
    ```
    http://127.0.0.1:8000/
    ```

## Usage

- **Home:** Overview and navigation.
- **Resume Analysis:** Upload your resume and generate questions.
- **Interview Questions:** Generate questions by job title and other settings.
- **Live Interview:** Practice with video, emotion detection, and chat.
- **Admin:** (If enabled) Manage users and logs.

## Customization

- Edit templates
