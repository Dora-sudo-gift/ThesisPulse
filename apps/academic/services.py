from django.db import transaction
from .models import Subject, Project, Report

def submit_student_subject(student, title, abstract, keywords):
    
    subject = Subject.objects.create(
        student=student,
        title=title,
        abstract=abstract,
        keywords=keywords
    )
    
    
    evaluation = evaluate_subject_smart(abstract, keywords)
    
    subject.ai_score = evaluation["score"]
    subject.ai_strengths = evaluation["strengths"]
    subject.ai_alerts = evaluation["alerts"]
    subject.status = Subject.Status.AI_EVALUATED
    subject.save()
    
    return subject

def evaluate_subject_smart(abstract, keywords):
    
    text = (abstract + " " + keywords).lower()
    score = 70  # Score de base
    strengths = []
    alerts = []

    
    tech_stack = ['django', 'python', 'docker', 'postgresql', 'react', 'fastapi', 'tailwind', 'ai', 'nlp', 'rag']
    found_techs = [tech for tech in tech_stack if tech in text]
    
    if len(found_techs) >= 3:
        score += 15
        strengths.append(f"Excellente maîtrise technologique identifiée ({', '.join(found_techs)}). Architecture robuste.")
    else:
        score -= 10
        alerts.append("Stack technique un peu légère ou non explicitée. Précisez les technologies.")

    
    if any(word in text for word in ['gestion', 'plateforme', 'automatisation', 'sécurité', 'optimisation', 'santé', 'éducation', 'erp']):
        score += 15
        strengths.append("Le projet répond à un problème réel et mesurable de la société ou des entreprises.")
    else:
        alerts.append("Le problème sociétal ou professionnel cible mériterait d'être davantage clarifié dans l'abstract.")


    score = max(30, min(100, score))

    return {
        "score": score,
        "strengths": " • ".join(strengths) if strengths else "Proposition viable avec un bon potentiel d'implémentation.",
        "alerts": " • ".join(alerts) if alerts else "Aucune alerte majeure relevée par le système d'analyse."
    }

@transaction.atomic
def assign_supervisor_and_create_project(subject, supervisor, admin_user):
    
    subject.supervisor = supervisor
    subject.status = Subject.Status.ASSIGNED
    subject.save()
    
    project = Project.objects.create(
        subject=subject,
        student=subject.student,
        supervisor=supervisor,
        status='IN_PROGRESS'
    )
    
    return project

def handle_student_report_upload(project, uploaded_file, description=""):
    
    report = Report.objects.create(
        project=project,
        file=uploaded_file,
        description=description
    )
    
    
    return report