from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from django.contrib.auth import get_user_model
from django.db.models import Q
import json
from django.core.serializers.json import DjangoJSONEncoder

from apps.academic.models import Subject, Project
from apps.ai_module.matching import find_top_supervisors
from apps.scheduling.models import Event
from .solver import generate_defense_schedule 
from .pdf_generator import generate_pv_document 

User = get_user_model()

@login_required(login_url='login')
def admin_dashboard_view(request):
    if not request.user.is_superuser and getattr(request.user, 'role', '') != 'ADMIN' and not request.user.is_staff:
        return render(request, 'academic/access_denied.html')

    # 🔄 SYNCHRONISATION AUTOMATIQUE : Garantit que chaque sujet assigné a bien son objet Project créé et visible par l'encadrant !
    assigned_subs = Subject.objects.filter(supervisor__isnull=False)
    for s in assigned_subs:
        if s.status != 'ASSIGNED':
            s.status = 'ASSIGNED'
            s.save()
        Project.objects.update_or_create(
            student=s.student,
            defaults={
                'subject': s,
                'supervisor': s.supervisor,
                'status': 'IN_PROGRESS'
            }
        )

    if request.method == 'POST':
        
        # 1. Accepter un sujet (Passe le statut à ADMIN_VALIDATED et déverrouille le matching)
        if 'accept_subject' in request.POST:
            subject_id = request.POST.get('subject_id')
            subject = get_object_or_404(Subject, id=subject_id)
            subject.status = 'ADMIN_VALIDATED'
            subject.save()
            messages.success(request, f"Sujet '{subject.title}' accepté ! Vous pouvez maintenant assigner un encadrant.")
            return redirect('scheduling:admin_dashboard')

        # 2. Refuser un sujet (Passe le statut à REJECTED et notifie l'étudiant)
        elif 'reject_subject' in request.POST:
            subject_id = request.POST.get('subject_id')
            subject = get_object_or_404(Subject, id=subject_id)
            subject.status = 'REJECTED'
            subject.admin_comment = "Votre sujet a été rejeté par l'administration. Veuillez soumettre une nouvelle proposition."
            subject.save()
            messages.error(request, f"❌ Sujet '{subject.title}' refusé. Une croix a été apposée et une notification de refus a été envoyée à {subject.student.get_full_name() or subject.student.username}.")
            return redirect('scheduling:admin_dashboard')

        # 3. Assigner un encadrant à un sujet validé (Passe le statut à ASSIGNED, crée le projet et clôture les autres propositions de l'étudiant)
        elif 'assign_supervisor' in request.POST:
            subject_id = request.POST.get('subject_id')
            supervisor_id = request.POST.get('supervisor_id')
            
            subject = get_object_or_404(Subject, id=subject_id)
            supervisor = get_object_or_404(User, id=supervisor_id)
            
            subject.supervisor = supervisor
            subject.status = 'ASSIGNED'
            subject.save()

            Project.objects.update_or_create(
                student=subject.student,
                defaults={
                    'subject': subject,
                    'supervisor': supervisor,
                    'status': 'IN_PROGRESS'
                }
            )

            # 🛡️ RÈGLE MÉTIER : Refuser automatiquement les autres sujets en attente ou validés de CET étudiant pour éviter les doublons !
            Subject.objects.filter(student=subject.student).exclude(id=subject.id).update(
                status='REJECTED',
                admin_comment="Un autre sujet de vos propositions a déjà été officiellement validé et assigné par l'administration."
            )
            
            messages.success(request, f"Encadrant {supervisor.get_full_name() or supervisor.username} assigné avec succès à {subject.student.username}. Les autres propositions de cet étudiant ont été clôturées.")
            return redirect('scheduling:admin_dashboard')

        # 4. Lancer le solveur Google OR-Tools pour les soutenances et jurys
        elif 'run_scheduler' in request.POST:
            try:
                generate_defense_schedule()
                messages.success(request, "Planning des soutenances, salles et jurys par filière généré avec succès par Google OR-Tools.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la planification : {e}")
            return redirect('scheduling:admin_dashboard')

        # 5. Créer ou gérer un étudiant
        elif 'create_student' in request.POST:
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            age = request.POST.get('age')
            quartier = request.POST.get('quartier', '').strip()
            phone = request.POST.get('phone', '').strip()
            filiere = request.POST.get('filiere', '').strip()
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if password != confirm_password:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return redirect('scheduling:admin_dashboard')

            clean_first = first_name.lower().replace(' ', '')
            clean_last = last_name.lower().replace(' ', '')
            base_username = f"{clean_first}.{clean_last}"
            
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            email = f"{username}@ictu.cm"
            matricule = f"ICTU2026{User.objects.count() + 15}"

            student = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='STUDENT',
                filiere=filiere,
                age=int(age) if age and age.isdigit() else None,
                quartier=quartier,
                phone_number=phone,
                matricule=matricule,
                visible_password=password,
                is_active=True
            )
            student.set_password(password)
            student.save()
            messages.success(request, f"Étudiant {first_name} {last_name} créé avec succès (Identifiant de connexion : {username}).")
            return redirect('scheduling:admin_dashboard')

        # 6. Créer ou gérer un encadrant
        elif 'create_supervisor' in request.POST:
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            age = request.POST.get('age')
            quartier = request.POST.get('quartier', '').strip()
            phone = request.POST.get('phone', '').strip()
            specialites_list = request.POST.getlist('specialites')
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if password != confirm_password:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return redirect('scheduling:admin_dashboard')

            clean_first = first_name.lower().replace(' ', '')
            clean_last = last_name.lower().replace(' ', '')
            base_username = f"{clean_first}.{clean_last}"
            
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            email = f"{username}@ictu.cm"

            sup = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='SUPERVISOR',
                specialites=specialites_list,
                age=int(age) if age and age.isdigit() else None,
                quartier=quartier,
                phone_number=phone,
                visible_password=password,
                is_active=True
            )
            sup.set_password(password)
            sup.save()
            messages.success(request, f"Encadrant {first_name} {last_name} créé avec succès (Identifiant de connexion : {username}).")
            return redirect('scheduling:admin_dashboard')

        # 7. Supprimer un utilisateur
        elif 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')
            user_to_delete = get_object_or_404(User, id=user_id)
            full_name = user_to_delete.get_full_name() or user_to_delete.username
            user_to_delete.delete()
            messages.success(request, f"Le compte de {full_name} a été supprimé définitivement.")
            return redirect('scheduling:admin_dashboard')

        # 8. Créer un événement institutionnel
        elif 'create_event' in request.POST:
            title = request.POST.get('event_title')
            date = request.POST.get('event_date')
            desc = request.POST.get('event_desc')
            
            Event.objects.create(
                title=title,
                date=date,
                description=desc,
                created_by=request.user
            )
            messages.success(request, f"🔔 Événement '{title}' publié et notifié sur tous les dashboards.")
            return redirect('scheduling:admin_dashboard')

        # 9. Supprimer un événement
        elif 'delete_event' in request.POST:
            event_id = request.POST.get('event_id')
            ev = get_object_or_404(Event, id=event_id)
            ev.delete()
            messages.success(request, "Événement retiré du calendrier.")
            return redirect('scheduling:admin_dashboard')


    all_subjects = Subject.objects.all().order_by('-created_at')
    active_projects = Project.objects.select_related('student', 'supervisor', 'subject').all()
    all_students_list = User.objects.filter(role='STUDENT').exclude(is_superuser=True).order_by('-id')
    all_supervisors_list = User.objects.filter(role='SUPERVISOR').order_by('-id')
    all_events = Event.objects.all().order_by('date')

    subjects_with_matching = []
    for subj in all_subjects:
        top_matches = find_top_supervisors(subj) if not subj.supervisor else []
        subjects_with_matching.append({
            'subject': subj,
            'top_matches': top_matches
        })

    total_subjects = Subject.objects.count()
    validated_subjects = Subject.objects.filter(Q(status='ADMIN_VALIDATED') | Q(status='ASSIGNED')).count()
    assigned_subjects = Subject.objects.filter(status='ASSIGNED').count()
    rejected_subjects = Subject.objects.filter(status='REJECTED').count()
    pending_subjects = Subject.objects.exclude(
        status__in=['ADMIN_VALIDATED', 'ASSIGNED', 'REJECTED']
    ).count()

    events_json = json.dumps([
        {
            'id': ev.id,
            'title': ev.title,
            'date': ev.date.strftime('%Y-%m-%d'),
            'time': ev.date.strftime('%H:%M'),
            'description': ev.description or ''
        }
        for ev in all_events if ev.date
    ], cls=DjangoJSONEncoder)

    context = {
        'subjects_with_matching': subjects_with_matching,
        'active_projects': active_projects,
        'all_students_list': all_students_list,
        'all_supervisors_list': all_supervisors_list,
        'all_events': all_events,
        'events_json': events_json,
        'total_students': all_students_list.count(),
        'total_supervisors': all_supervisors_list.count(),
        'total_subjects': total_subjects,
        'validated_subjects': validated_subjects,
        'assigned_subjects': assigned_subjects,
        'rejected_subjects': rejected_subjects,
        'pending_subjects': pending_subjects,
    }

    return render(request, 'scheduling/admin_dashboard.html', context)


@login_required(login_url='login')
def schedule_dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return render(request, 'academic/access_denied.html')
        
    projects = Project.objects.all()
    context = {
        'projects': projects,
    }
    return render(request, 'scheduling/schedule_dashboard.html', context)


@login_required(login_url='login')
def download_pv_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    

    if not (request.user.is_staff or request.user == project.supervisor or request.user == project.student or getattr(request.user, 'is_jury_member', False)):
        return render(request, 'academic/access_denied.html')

    pdf_path = generate_pv_document(project)
    
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=f"PV_Soutenance_{project.student.username}.pdf")