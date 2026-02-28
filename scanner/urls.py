from django.urls import path
from .views import upload_resume, recruiter_dashboard, result_page, scan_status, scan_progress

urlpatterns = [
    path('', upload_resume, name='upload_resume'),
    path('dashboard/', recruiter_dashboard, name='dashboard'),
    path("result/<int:id>/", result_page, name="result_page"),
    path("scan-status/<int:id>/", scan_status, name="scan_status"),
    path("scan-progress/<int:id>/", scan_progress, name="scan_progress"),

]