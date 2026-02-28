# ATS Resume Scanner (Django + Celery)

## Overview

ATS Resume Scanner is a production-style Applicant Tracking System (ATS) web application built using **Django**, **Celery**, and **Redis**. The platform allows candidates to upload resumes, automatically evaluates resumes against job descriptions, and provides recruiters with ranked candidate dashboards and alerts for high‑match candidates.

---

## Key Features

### Candidate Features

* Resume upload (PDF only, size limited)
* Automated ATS scoring based on job description
* Missing skill detection (skills gap analysis)
* Email notification with ATS results
* Real‑time scanning progress updates

### Recruiter Features

* Recruiter dashboard with ranked candidates
* Filter candidates by:

  * ATS score
  * Job title
  * Missing skills
  * Candidate name/email
* Top candidate per job display
* High‑match candidate email alerts

### System Architecture

* Django backend (web + API)
* Celery async task queue for resume processing
* Redis message broker
* S3 storage support for resume files
* SMTP email notifications

---

## Tech Stack

* Python 3.13
* Django 6
* Celery
* Redis
* PostgreSQL / SQLite (dev)
* AWS S3 (optional storage)
* HTML / CSS frontend templates

---

## Installation

### 1. Clone repository

```bash
git clone https://github.com/yourusername/ats-scanner.git
cd ats-scanner
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start Redis

```bash
redis-server
```

### 6. Start Celery worker

```bash
celery -A ats_scanner worker -l info
```

### 7. Run Django server

```bash
python manage.py runserver
```

---

## Environment Variables

Configure the following in `settings.py` or environment variables:

* Email SMTP credentials
* AWS S3 credentials (optional)
* Recruiter notification email list
* ATS alert score threshold

Example:

```python
ATS_ALERT_THRESHOLD = 80
RECRUITER_NOTIFICATION_EMAILS = ["recruiter@company.com"]
```

---

## Application Workflow

1. Candidate uploads resume
2. Resume processing is sent to Celery queue
3. Worker extracts resume text
4. ATS score and skill gaps are calculated
5. Candidate receives result email
6. Recruiters receive alert if candidate exceeds threshold
7. Dashboard automatically updates rankings

---

## Future Enhancements

* Job posting management module
* AI‑based semantic resume scoring
* Candidate ranking intelligence engine
* WebSocket real‑time notifications
* Multi‑tenant recruiter support

---

## License

MIT License
