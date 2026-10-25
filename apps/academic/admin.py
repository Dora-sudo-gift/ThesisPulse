from django.contrib import admin
from .models import Subject, Project, Milestone, Report

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'status', 'ai_score', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'student__username', 'student__email')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('subject', 'student', 'supervisor', 'status', 'final_grade')

admin.site.register(Milestone)
admin.site.register(Report)