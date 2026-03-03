import requests
from .utils import calculate_ats_score

OLLAMA_URL = "http://localhost:11434/api/generate"


def call_ollama(prompt, model="llama3:8b"):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


def generate_and_optimize_cv(data, job_description):

    # Step 1: Generate initial CV
    initial_prompt = f"""
    Create a professional ATS-friendly resume.

    Name: {data.get('name', '')}
    Role: {data.get('role', '')}
    Experience: {data.get('experience', '')}
    Skills: {data.get('skills', '')}
    Education: {data.get('education', '')}
    Certifications: {data.get('certifications', '')}
    Projects: {data.get('projects', '')}
    Achievements: {data.get('achievements', '')}

    Rules:
    - Use measurable achievements
    - No tables
    - Clean formatting
    """

    cv_text = call_ollama(initial_prompt)

    # Step 2: Score it using YOUR ATS logic
    score = calculate_ats_score(cv_text, job_description)

    # Step 3: Improve if weak
    if score < 75:
        improve_prompt = f"""
        Improve this resume to better match the job description.

        JOB DESCRIPTION:
        {job_description}

        CURRENT RESUME:
        {cv_text}

        Increase keyword alignment and measurable achievements.
        """

        cv_text = call_ollama(improve_prompt)
        score = calculate_ats_score(cv_text, job_description)

    return cv_text, score