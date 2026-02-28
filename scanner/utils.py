from pdfminer.high_level import extract_text
from docx import Document
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from sklearn.feature_extraction.text import CountVectorizer
import tempfile
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


print("Loading SentenceTransformer model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Model loaded successfully.")


ACTION_VERBS = {
    "led", "designed", "architected", "implemented",
    "developed", "optimized", "delivered", "managed"
}


# ================================
# Utility Functions
# ================================

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text


def extract_keywords_from_jd(job_description):
    """
    Extract meaningful keywords from job description.
    Removes stopwords and short tokens.
    """
    stopwords = {
        "the", "and", "with", "for", "that",
        "this", "are", "you", "your", "will",
        "have", "has", "our", "from", "but",
        "all", "any", "not", "can", "who"
    }

    words = re.findall(r'\b[a-zA-Z0-9]+\b', job_description.lower())

    keywords = {
        word for word in words
        if word not in stopwords and len(word) > 2
    }

    return keywords


def extract_required_keywords(job_description):
    """
    Extract keywords from lines containing
    'required', 'must', 'mandatory'
    """
    required_keywords = set()
    lines = job_description.lower().split("\n")

    for line in lines:
        if any(tag in line for tag in ["required", "must", "mandatory"]):
            words = re.findall(r'\b[a-zA-Z0-9]+\b', line)
            required_keywords.update(words)

    return required_keywords


# ================================
# Enterprise ATS Scoring
# ================================

def calculate_ats_score(resume_text, job_description):

    if not model:
        return 0.0

    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)

    resume_words = set(resume_text.split())

    jd_keywords = extract_keywords_from_jd(job_description)
    required_keywords = extract_required_keywords(job_description)

    # ===============================
    # 1️⃣ Semantic Similarity (45%)
    # ===============================

    resume_embedding = model.encode([resume_text], normalize_embeddings=True)
    job_embedding = model.encode([job_description], normalize_embeddings=True)

    similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]

    semantic_score = max(0, (similarity - 0.25) / (0.85 - 0.25))
    semantic_score = min(semantic_score, 1)

    # ===============================
    # 2️⃣ Required Coverage (25%)
    # ===============================

    if required_keywords:
        matched_required = required_keywords.intersection(resume_words)
        required_score = len(matched_required) / len(required_keywords)
    else:
        required_score = 0.6  # neutral default

    # ===============================
    # 3️⃣ General Keyword Coverage (15%)
    # ===============================

    matched_keywords = jd_keywords.intersection(resume_words)

    keyword_score = (
        len(matched_keywords) / len(jd_keywords)
        if jd_keywords else 0
    )

    # ===============================
    # 4️⃣ Keyword Density (5%)
    # ===============================

    density_count = sum(resume_text.count(word) for word in jd_keywords)
    density_score = min(density_count / 20, 1)

    # ===============================
    # 5️⃣ Impact Score (10%)
    # ===============================

    verb_hits = sum(1 for verb in ACTION_VERBS if verb in resume_text)
    metrics_hits = len(re.findall(r'\b\d+%?\b', resume_text))

    impact_score = min((verb_hits + metrics_hits) / 10, 1)

    # ===============================
    # Final Score
    # ===============================

    final_score = (
        (0.45 * semantic_score) +
        (0.25 * required_score) +
        (0.15 * keyword_score) +
        (0.05 * density_score) +
        (0.10 * impact_score)
    )

    return round(final_score * 100, 2)

def extract_resume_text(file):

    filename = file.name.lower()   

    # PDF handling
    if filename.endswith(".pdf"):
        file.open()
        file.seek(0)

        with tempfile.NamedTemporaryFile(delete=True) as temp:
            temp.write(file.read())
            temp.flush()
            return extract_text(temp.name)

    # DOCX (optional)
    elif filename.endswith(".docx"):
        file.open()
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    return ""

def extract_keywords(text):
    if not text or not text.strip():
        return set()

    text = re.sub(r'[^a-zA-Z ]', ' ', text.lower())

    try:
        vectorizer = CountVectorizer(stop_words='english')
        vectorizer.fit([text])
        return set(vectorizer.get_feature_names_out())
    except ValueError:
        # empty vocabulary case
        return set()


def find_missing_keywords(resume_text, job_description):
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)

    if not jd_keywords:
        return []

    missing = jd_keywords - resume_keywords
    return list(missing)[:20]


def generate_recommendations(resume_text, job_description, score):

    recommendations = []

    # Always give guidance under 75%
    if score < 75:
        recommendations.append({
            "priority": "High",
            "message": "Tailor your resume more closely to the job description by mirroring its terminology.",
            "impact": "+8–15%"
        })

    if score < 60:
        recommendations.append({
            "priority": "Medium",
            "message": "Strengthen your professional summary to clearly match the role requirements.",
            "impact": "+5–10%"
        })

    if score < 50:
        recommendations.append({
            "priority": "Critical",
            "message": "Rewrite experience bullets to directly align with required skills.",
            "impact": "+15–25%"
        })

    # Metrics check
    if not re.search(r'\b\d+%?\b', resume_text):
        recommendations.append({
            "priority": "Medium",
            "message": "Add measurable achievements (e.g., improved performance by 30%).",
            "impact": "+5%"
        })

    # Action verbs check
    verb_hits = sum(1 for verb in ACTION_VERBS if verb in resume_text.lower())
    if verb_hits < 3:
        recommendations.append({
            "priority": "Low",
            "message": "Use stronger action verbs such as led, architected, optimized.",
            "impact": "+3–5%"
        })

    # Fallback
    if not recommendations:
        recommendations.append({
            "priority": "Optimization",
            "message": "Your resume is strong but could still be further aligned with the job.",
            "impact": "+2–4%"
        })

    return recommendations