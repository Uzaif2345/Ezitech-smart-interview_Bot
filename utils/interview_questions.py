INTERVIEW_QUESTIONS = {
    "AI Research Assistant": [
        "What is the difference between supervised and unsupervised learning?",
        "Explain how backpropagation works in neural networks.",
        "What are activation functions, and why are they important?"
    ],
    "Data Analyst Intern": [
        "What is the difference between Excel VLOOKUP and INDEX/MATCH?",
        "How would you deal with missing data in a dataset?",
        "What tools have you used for data visualization?"
    ],
    "Frontend Developer": [
        "What is the Virtual DOM in React?",
        "Explain how CSS Grid and Flexbox differ.",
        "What is the difference between var, let, and const in JavaScript?"
    ]
}

def get_questions_for_job(job_title):
    return INTERVIEW_QUESTIONS.get(job_title, ["No questions found."])