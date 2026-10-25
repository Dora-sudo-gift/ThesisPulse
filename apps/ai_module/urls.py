from django.urls import path
from . import views

app_name = 'ai_module'

urlpatterns = [
    path('supervisor/dashboard/', views.supervisor_dashboard_view, name='supervisor_dashboard'),
    path('project/<int:project_id>/rag-chat/', views.project_rag_chat_view, name='rag_chat'),
]