# scanner/views.py
from django.shortcuts import render
from .models import Resume
from .utils import (
    extract_resume_text,
    calculate_ats_score,
    find_missing_keywords   
)
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import Resume
from .tasks import scan_resume_task
from django.db.models import Max
from django.http import FileResponse
from .models import Resume

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.core.mail import EmailMessage
from decimal import Decimal



def upload_resume(request):
    if request.method == "POST":

        experience = request.POST.get("experience_years")
        salary = request.POST.get("expected_salary")

        resume = Resume.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            resume_file=request.FILES.get("resume"),
            job_title=request.POST.get("job_title"),
            job_description=request.POST.get("jd"),
            experience_years=int(experience) if experience else None,
            expected_salary=Decimal(salary) if salary else None,
            status="uploading"
        )

        # Send to background worker
        scan_resume_task.delay(resume.id)

        return redirect("scan_progress", id=resume.id)

    return render(request, "upload.html")


@login_required(login_url='/accounts/login/')
def recruiter_dashboard(request):

    query = request.GET.get("q", "")
    min_score = request.GET.get("score", "")
    job_title = request.GET.get("job", "")
    skill = request.GET.get("skill", "")

    resumes = Resume.objects.all().order_by("-score")

    if query:
        resumes = resumes.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query)
        )

    if min_score:
        resumes = resumes.filter(score__gte=min_score)

    if job_title:
        resumes = resumes.filter(job_title__icontains=job_title)

    if skill:
        resumes = resumes.filter(missing_keywords__icontains=skill)

    # -------- Top candidate per job (SQLite compatible) --------
    top_candidates_dict = {}
    for r in Resume.objects.order_by("-score"):
        if r.job_title not in top_candidates_dict:
            top_candidates_dict[r.job_title] = r

    top_candidates = list(top_candidates_dict.values())
    # ----------------------------------------------------------

    return render(request, "dashboard.html", {
        "resumes": resumes,
        "job_title": job_title,
        "skill": skill,
        "top_candidates": top_candidates
    })



def result_page(request, id):
    resume = Resume.objects.get(id=id)

    recommendations = []

    if resume.score_breakdown:
        recommendations = resume.score_breakdown.get("recommendations", [])

    return render(request, "result.html", {
        "score": resume.score,
        "missing_keywords": resume.missing_keywords or [],
        "recommendations": recommendations
    })


def scan_status(request, id):
    resume = Resume.objects.get(id=id)

    return JsonResponse({
        "status": resume.status,
        "score": resume.score
    })

def scan_progress(request, id):
    return render(request, "scan_progress.html", {"resume_id": id})



def download_optimized(request, resume_id):
    resume = Resume.objects.get(id=resume_id)

    if not resume.optimized_file:
        return HttpResponse("File not generated yet.")

    return FileResponse(
        resume.optimized_file.open(),
        as_attachment=True,
        filename="ATS_Optimized_Resume.docx"
    )


@csrf_exempt
def generate_cv_view(request):

    if request.method == "POST":

        data = json.loads(request.body)

        # 1️⃣ Build structured resume
        structured_data = build_structured_cv(data)

        # 2️⃣ Generate DOCX
        file_name = generate_ats_docx_from_data(structured_data)

        file_path = os.path.join(os.getcwd(), file_name)

        # 3️⃣ Send Email
        email = EmailMessage(
            subject="Your Generated ATS-Optimized CV",
            body=f"""
Hi {data['name']},

Your ATS-optimized CV for the role of {data['target_role']} is attached.

Best regards,
Job200
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[data["email"]],
        )

        email.attach_file(file_path)
        email.send()

        return JsonResponse({
            "status": "success",
            "message": "CV generated and sent to your email."
        })

    return JsonResponse({"error": "Invalid request"})


def cv_form_view(request):
    return render(request, "generate_cv.html")