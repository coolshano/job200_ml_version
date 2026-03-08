import requests
import json
import re
from .utils import calculate_ats_score

OLLAMA_URL = "http://localhost:11434/api/generate"


def call_ollama(prompt, model="mistral"):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.4
            },
            timeout=300
        )

        response.raise_for_status()
        data = response.json()

        # Debug safety log (remove later)
        if "response" not in data:
            print("Unexpected Ollama response:", data)
            return ""

        return data["response"]

    except requests.exceptions.Timeout:
        print("Ollama request timed out")
        return ""

    except requests.exceptions.RequestException as e:
        print("Ollama request failed:", str(e))
        return ""

    except Exception as e:
        print("Unexpected Ollama error:", str(e))
        return ""


def extract_json(text):
    """
    Extract JSON block from LLM response safely.
    """
    try:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)

        if json_match:
            return json.loads(json_match.group())

    except Exception:
        pass

    return None


def generate_and_optimize_cv(data, job_description):

    initial_prompt = f"""
You are a professional resume writer.

Return ONLY valid JSON.

Do NOT include explanations.
Do NOT include markdown.
Do NOT include text before or after JSON.

JSON structure:

{{
 "summary": "",
 "experience": [
   "Job Title — Company (Dates)",
   "Achievement bullet point"
 ],
 "skills": [],
 "education": "Degree — University (Year)",
 "certifications": [],
 "projects": [],
 "achievements": []
}}

Formatting rules:

Experience must contain readable bullet points such as:
"Senior DevOps Engineer — Virtusa (2022–Present)"
"Implemented CI/CD pipeline reducing deployment time by 40%"

Education must be written like:
"BSc Computer Science — University of Colombo (2020)"

Skills must be short items like:
"AWS"
"Docker"
"Kubernetes"

Candidate Information:

Name: {data.get('name','')}
Target Role: {data.get('role','')}

Experience:
{data.get('experience','')}

Skills:
{data.get('skills','')}

Education:
{data.get('education','')}

Certifications:
{data.get('certifications','')}

Projects:
{data.get('projects','')}

Achievements:
{data.get('achievements','')}
"""

    response = call_ollama(initial_prompt)

    resume_data = extract_json(response)

    if not resume_data:
        resume_data = {
            "summary": response,
            "experience": [],
            "skills": [],
            "education": "",
            "certifications": [],
            "projects": [],
            "achievements": []
        }

    # Normalize missing fields
    resume_data.setdefault("summary", "")
    resume_data.setdefault("experience", [])
    resume_data.setdefault("skills", [])
    resume_data.setdefault("education", "")
    resume_data.setdefault("certifications", [])
    resume_data.setdefault("projects", [])
    resume_data.setdefault("achievements", [])

    resume_text = json.dumps(resume_data)

    score = calculate_ats_score(resume_text, job_description)

    if score < 75:

        improve_prompt = f"""
Improve the following resume so it better matches the job description.

Return ONLY JSON using the SAME format.

Important rules:

Experience must remain readable bullet points like:
"DevOps Engineer — ABC Corp (2021–Present)"
"Reduced deployment failures by 35%"

Education must remain:
"Degree — University (Year)"

JOB DESCRIPTION:
{job_description}

CURRENT RESUME:
{json.dumps(resume_data)}
"""

        improved_response = call_ollama(improve_prompt)

        improved_data = extract_json(improved_response)

        if improved_data:
            resume_data.update(improved_data)

        resume_text = json.dumps(resume_data)

        score = calculate_ats_score(resume_text, job_description)

    return resume_data, score