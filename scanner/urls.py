from django.urls import path
from .views import upload_resume, recruiter_dashboard, result_page

urlpatterns = [
    path('', upload_resume, name='upload_resume'),
    path('dashboard/', recruiter_dashboard, name='dashboard'),
    path('result/', result_page, name='result_page'),
]