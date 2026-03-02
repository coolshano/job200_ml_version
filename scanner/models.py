from django.db import models
from django.core.exceptions import ValidationError
import os

def validate_pdf(file):

    # Extension check
    ext = os.path.splitext(file.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError("Only PDF files are allowed.")

    # MIME type check (if available)
    content_type = getattr(file, "content_type", None)
    if content_type and content_type != 'application/pdf':
        raise ValidationError("Invalid file type. Upload a valid PDF.")

    # File size check (5 MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError("File size must be under 5 MB.")



class Resume(models.Model):

    name = models.CharField(max_length=200)
    email = models.EmailField()
    job_title = models.CharField(max_length=200)

    resume_file = models.FileField(upload_to="resumes/")
    job_description = models.TextField()

    score = models.FloatField(null=True, blank=True)
    missing_keywords = models.JSONField(null=True, blank=True)

    parsed_data = models.JSONField(null=True, blank=True)
    score_breakdown = models.JSONField(null=True, blank=True)

    optimized_file = models.FileField(
        upload_to="optimized/",
        null=True,
        blank=True
    )

    experience_years = models.FloatField(null=True, blank=True)

    expected_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    score_breakdown = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=30, default="uploading")
    created_at = models.DateTimeField(auto_now_add=True)