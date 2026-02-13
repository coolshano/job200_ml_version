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
    resume_file = models.FileField(
        upload_to='resumes/',
        validators=[validate_pdf]
    )
    job_description = models.TextField()
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)