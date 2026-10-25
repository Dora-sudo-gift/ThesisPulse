from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from thesis_pulse.views import login_view, forgot_password_view, logout_view

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('programs/', TemplateView.as_view(template_name='programs.html'), name='programs'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    
    
    path('login/', login_view, name='login'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('logout/', logout_view, name='logout'),

    path('admin/', admin.site.urls),
    path('academic/', include('apps.academic.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('scheduling/', include('apps.scheduling.urls')),
    path('ai/', include('apps.ai_module.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)