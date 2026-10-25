from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    path('dashboard/', views.schedule_dashboard, name='schedule_dashboard'),
    path('pv/<int:project_id>/download/', views.download_pv_view, name='download_pv'),
    
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]