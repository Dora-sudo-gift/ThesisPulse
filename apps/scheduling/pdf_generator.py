import os
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pv_document(project):
    
    pv_dir = os.path.join(settings.MEDIA_ROOT, 'pvs')
    os.makedirs(pv_dir, exist_ok=True)
    
    file_path = os.path.join(pv_dir, f"PV_Projet_{project.id}.pdf")
    
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=20
    )
    
    story.append(Paragraph("THE ICT UNIVERSITY - PROCÈS-VERBAL DE SOUTENANCE", title_style))
    story.append(Spacer(1, 15))

    
    student_name = f"<b>Étudiant(e) :</b> {project.student.get_full_name() or project.student.username}"
    project_title = f"<b>Intitulé du PFE :</b> {project.subject.title}"
    supervisor_name = f"<b>Encadrant :</b> {project.supervisor.get_full_name() if project.supervisor else 'Non assigné'}"
    final_grade = f"<b>Note Finale Attribuée :</b> {project.final_grade if project.final_grade is not None else 'En attente de délibération'}"

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10
    )

    story.append(Paragraph(student_name, body_style))
    story.append(Paragraph(project_title, body_style))
    story.append(Paragraph(supervisor_name, body_style))
    story.append(Paragraph(final_grade, body_style))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("<i>Document généré automatiquement par la plateforme ThesisPulse.</i>", styles['Italic']))

    doc.build(story)
    return file_path