from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Subject, Project, Milestone, Report, GroupMessage
from apps.scheduling.models import Event, DefenseSchedule
from apps.ai_module.smart_sujet import evaluate_subject_abstract
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required(login_url='login')
def student_dashboard_view(request):
    user = request.user

    
    subjects = Subject.objects.filter(student=user).order_by('-created_at')
    
    
    try:
        project = Project.objects.select_related('supervisor', 'subject').get(student=user)
        milestones = project.milestones.all()
        reports = project.reports.all().order_by('-uploaded_at')
        assigned_supervisor = project.supervisor
    except Project.DoesNotExist:
        project = None
        milestones = []
        reports = []
        
        assigned_subject = subjects.filter(Q(status='ASSIGNED') | Q(status='ADMIN_VALIDATED'), supervisor__isnull=False).first()
        assigned_supervisor = assigned_subject.supervisor if assigned_subject else None

    group_messages = []
    group_members = []
    if assigned_supervisor:
        group_messages = GroupMessage.objects.filter(supervisor=assigned_supervisor).select_related('sender').order_by('created_at')
        group_members = User.objects.filter(
            Q(role='STUDENT', assigned_subjects__supervisor=assigned_supervisor) |
            Q(id=assigned_supervisor.id)
        ).distinct()

    events = Event.objects.all().order_by('date')


    student_defense = None
    if project:
        student_defense = DefenseSchedule.objects.filter(project=project, is_published=True).select_related('room').prefetch_related('jury_members').first()

    total_submitted = subjects.count()
    total_accepted = subjects.filter(Q(status='ADMIN_VALIDATED') | Q(status='ASSIGNED')).count()
    total_rejected = subjects.filter(status='REJECTED').count()
    accepted_subject = subjects.filter(Q(status='ADMIN_VALIDATED') | Q(status='ASSIGNED')).first()

    if request.method == 'POST':
        
        if 'submit_subject' in request.POST:
            
            if subjects.filter(status__in=['ADMIN_VALIDATED', 'ASSIGNED']).exists() or (project is not None):
                messages.error(request, "Vous possédez déjà un sujet validé ou assigné par l'administration. Il n'est plus possible de soumettre de nouvelles propositions.")
                return redirect('academic:student_dashboard')

            title = request.POST.get('title', '').strip()
            abstract = request.POST.get('abstract', '').strip()
            architecture_details = request.POST.get('architecture_details', '').strip()
            time_feasibility = request.POST.get('time_feasibility', '').strip()
            keywords = request.POST.get('keywords', '').strip()

            if not title or not abstract:
                messages.error(request, "Veuillez remplir le titre et le résumé du projet.")
                return redirect('academic:student_dashboard')

            ai_analysis = evaluate_subject_abstract(
                abstract=abstract,
                keywords=keywords,
                title=title,
                architecture_details=architecture_details,
                time_feasibility=time_feasibility
            )

            Subject.objects.create(
                student=user,
                title=title,
                abstract=abstract,
                architecture_details=architecture_details,
                time_feasibility=time_feasibility,
                keywords=keywords,
                ai_score=ai_analysis['score'],
                ai_strengths=ai_analysis['strengths'],
                ai_alerts=ai_analysis['alerts'],
                status='AI_EVALUATED'
            )
            messages.success(request, f"🚀 Sujet soumis avec succès ! Score SmartSujet IA : {ai_analysis['score']}%")
            return redirect('academic:student_dashboard')

        elif 'upload_report' in request.POST:
            report_title = request.POST.get('report_title', '').strip()
            report_file = request.FILES.get('report_file')
            report_description = request.POST.get('report_description', '').strip()

            if not report_file or not project:
                messages.error(request, "Erreur : Veuillez sélectionner un fichier valide et vous assurer que votre projet est actif.")
                return redirect('academic:student_dashboard')

            report = Report.objects.create(
                project=project,
                file=report_file,
                description=f"[{report_title}] {report_description}"
            )
            messages.success(request, f"📨 Rapport transmis avec succès ! Attribué à l'identifiant #ID-{report.id}.")
            return redirect('academic:student_dashboard')

        elif 'send_group_message' in request.POST:
            content = request.POST.get('message_content', '').strip()
            if content and assigned_supervisor:
                GroupMessage.objects.create(
                    supervisor=assigned_supervisor,
                    sender=user,
                    content=content
                )
                messages.success(request, "Message envoyé dans le groupe !")
            else:
                messages.error(request, "Impossible d'envoyer un message vide ou aucun encadrant assigné.")
            return redirect('academic:student_dashboard')

        elif 'update_profile' in request.POST:
            phone_number = request.POST.get('phone_number', '').strip()
            quartier = request.POST.get('quartier', '').strip()
            age = request.POST.get('age')

            user.phone_number = phone_number
            user.quartier = quartier
            user.age = int(age) if age and age.isdigit() else None
            user.save()
            messages.success(request, "Vos informations de profil ont été mises à jour avec succès.")
            return redirect('academic:student_dashboard')

    context = {
        'subjects': subjects,
        'project': project,
        'milestones': milestones,
        'reports': reports,
        'events': events,
        'assigned_supervisor': assigned_supervisor,
        'group_messages': group_messages,
        'group_members': group_members,
        'total_submitted': total_submitted,
        'total_accepted': total_accepted,
        'total_rejected': total_rejected,
        'accepted_subject': accepted_subject,
        'student_defense': student_defense, 
    }
    return render(request, 'academic/student_dashboard.html', context)