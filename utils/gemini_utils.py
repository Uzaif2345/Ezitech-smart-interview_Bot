# utils/gemini_api.py

import google.generativeai as genai

# ✅ Your API key
GENAI_API_KEY = "AIzaSyC_tnA1s6YN7KWASylLWXzeU9PCFuGiVcE"
genai.configure(api_key=GENAI_API_KEY)

# Load Gemini Flash model
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_interview_questions(prompt, language='en'):
    try:
        lang_prefix = "Generate 3 job interview questions in Urdu." if language == 'ur' else "Generate 3 job interview questions in English."
        full_prompt = f"{lang_prefix} The job title or resume summary is: {prompt}"

        response = model.generate_content(full_prompt)
        return response.text.strip().split('\n')
    except Exception as e:
        return [f"[Error] Failed to generate questions: {str(e)}"]

def get_feedback(answer, language='en'):
    try:
        lang_prefix = "Give constructive feedback in Urdu." if language == 'ur' else "Give constructive feedback in English."
        prompt = f"{lang_prefix} Here's the candidate's answer: {answer}"

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Error] Failed to generate feedback: {str(e)}"
def generate_questions_with_gemini(job_title, language='en'):
    # Your Gemini API logic here
    ...
