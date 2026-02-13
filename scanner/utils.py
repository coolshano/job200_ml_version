from pdfminer.high_level import extract_text
from docx import Document
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from sklearn.feature_extraction.text import CountVectorizer
import tempfile



def calculate_ats_score(resume_text, job_description):

    # Cosine similarity (base relevance)
    cv = CountVectorizer().fit_transform([resume_text, job_description])
    cosine_score = cosine_similarity(cv)[0][1]

    # Keyword coverage score
    jd_words = set(job_description.lower().split())
    resume_words = set(resume_text.lower().split())

    matched_keywords = jd_words.intersection(resume_words)

    if len(jd_words) == 0:
        coverage_score = 0
    else:
        coverage_score = len(matched_keywords) / len(jd_words)

    # Weighted scoring (enterprise-style)
    final_score = (0.6 * cosine_score) + (0.4 * coverage_score)

    return round(final_score * 100, 2)



def extract_resume_text(file):

    filename = file.name.lower()   # FIX: use file.name

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
    text = re.sub(r'[^a-zA-Z ]', ' ', text.lower())

    vectorizer = CountVectorizer(stop_words='english')
    vectorizer.fit([text])

    return set(vectorizer.get_feature_names_out())


def find_missing_keywords(resume_text, job_description):
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)

    missing = jd_keywords - resume_keywords
    return list(missing)[:20]  