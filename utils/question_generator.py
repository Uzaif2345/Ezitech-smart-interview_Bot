# utils/question_generator.py

import spacy
import random

from utils import resume_parser

nlp = spacy.load("en_core_web_sm")  # Make sure it's installed!

def extract_keywords(text):
    doc = nlp(text)
    keywords = []

    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 2:
            keywords.append(token.text.lower())

    return list(set(keywords))  # Remove duplicates

def generate_questions_from_resume(resume_text, lang="en"):
    parsed = resume_parser.parse_resume(resume_text)
    questions = []

    if lang == "ur":
        questions.append(f"آپ کا نام {parsed['name']} ہے؟ براہ کرم اپنا تعارف کروائیں۔")
        if parsed['skills']:
            questions.append(f"آپ کی مہارتیں: {', '.join(parsed['skills'])}. ان میں سے سب سے اہم کون سی ہے؟")
        if parsed['projects']:
            questions.append(f"اپنے پراجیکٹ '{parsed['projects'][0]}' کے بارے میں بتائیں۔")
        questions.append("آپ اس جاب میں کیوں دلچسپی رکھتے ہیں؟")
    else:
        questions.append(f"Is your name {parsed['name']}? Please introduce yourself.")
        if parsed['skills']:
            questions.append(f"Your skills include: {', '.join(parsed['skills'])}. Which is your strongest?")
        if parsed['projects']:
            questions.append(f"Tell me about your project '{parsed['projects'][0]}'.")
        questions.append("Why are you interested in this job?")

    return questions

def generate_questions(num=5):
    sample = [
        "Tell me about yourself.",
        "Why should we hire you?",
        "Describe a challenge you've overcome.",
        "Where do you see yourself in 5 years?",
        "What is your greatest strength?",
    ]
    return sample[:num]
def get_sample_questions():
    return [
        {"text_en": "Tell me about your latest project.", "text_ur": "اپنے حالیہ پروجیکٹ کے بارے میں بتائیں۔"},
        {"text_en": "What are your key strengths?", "text_ur": "آپ کی اہم خوبیاں کیا ہیں؟"},
        {"text_en": "Why should we hire you?", "text_ur": "ہم آپ کو کیوں منتخب کریں؟"},
    ]

def generate_questions_from_resume(job_title, language="en", experience_level="mid", count=10):
    base_questions_en = [
        f"What skills are important for a {job_title}?",
        f"Describe your experience relevant to {job_title}.",
        f"Why are you interested in the {job_title} position?",
        f"How do you stay updated in the {job_title} field?",
        f"Describe a challenge you faced as a {job_title} and how you overcame it.",
        f"What tools or technologies do you use as a {job_title}?",
        f"How do you handle tight deadlines in your {job_title} work?",
        f"How do you prioritize tasks as a {job_title}?",
        f"Describe a successful project you completed as a {job_title}.",
        f"How do you handle feedback in your {job_title} role?"
    ]
    base_questions_ur = [
        f"{job_title} کے لیے کون سی مہارتیں اہم ہیں؟",
        f"اپنے {job_title} کے تجربے کے بارے میں بتائیں۔",
        f"آپ اس {job_title} پوزیشن میں کیوں دلچسپی رکھتے ہیں؟",
        f"آپ {job_title} کے شعبے میں کیسے اپڈیٹ رہتے ہیں؟",
        f"ایک چیلنج بیان کریں جو آپ نے {job_title} کے طور پر حل کیا۔",
        f"آپ {job_title} کے طور پر کون سے ٹولز یا ٹیکنالوجیز استعمال کرتے ہیں؟",
        f"آپ اپنے {job_title} کام میں ڈیڈ لائنز کو کیسے ہینڈل کرتے ہیں؟",
        f"آپ {job_title} کے طور پر کاموں کو کیسے ترجیح دیتے ہیں؟",
        f"ایک کامیاب پراجیکٹ بیان کریں جو آپ نے {job_title} کے طور پر مکمل کیا۔",
        f"آپ اپنے {job_title} رول میں فیڈبیک کو کیسے ہینڈل کرتے ہیں؟"
    ]
    questions = base_questions_en if language == "en" else base_questions_ur
    return questions[:count]
