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


def upload_resume(request):
    if request.method == "POST":
        resume = Resume.objects.create(
            name=request.POST["name"],
            email=request.POST["email"],
            resume_file=request.FILES["resume"],
            job_title=request.POST["job_title"],
            job_description=request.POST["jd"]
        )

        # IMPORTANT: open file and reset pointer for S3 storage
        resume.resume_file.open()
        resume.resume_file.seek(0)

        text = extract_resume_text(resume.resume_file)

        score = calculate_ats_score(text, resume.job_description)
        missing_keywords = find_missing_keywords(text, resume.job_description)

        resume.score = score
        resume.save()

        request.session["score"] = score
        request.session["missing_keywords"] = missing_keywords

        return redirect("result_page")

    return render(request, "upload.html")

@login_required(login_url='/accounts/login/')
def recruiter_dashboard(request):

    query = request.GET.get("q", "")
    min_score = request.GET.get("score", "")
    job_title = request.GET.get("job", "")   # NEW

    resumes = Resume.objects.all().order_by("-score")

    if query:
        resumes = resumes.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query)
        )

    if min_score:
        resumes = resumes.filter(score__gte=min_score)

    # NEW filter
    if job_title:
        resumes = resumes.filter(job_title__icontains=job_title)

    return render(request, "dashboard.html", {
        "resumes": resumes,
        "job_title": job_title
    })



def result_page(request):
    score = request.session.get("score")
    missing_keywords = request.session.get("missing_keywords")

    return render(request, "result.html", {   
        "score": score,
        "missing_keywords": missing_keywords
    })