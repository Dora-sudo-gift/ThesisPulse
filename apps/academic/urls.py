from django.urls import path
from .views import student_dashboard_view

app_name = 'academic'

urlpatterns = [
    path('dashboard/', student_dashboard_view, name='student_dashboard'),
]