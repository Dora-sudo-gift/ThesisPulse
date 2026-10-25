from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from auditlog.registry import auditlog

class Subject(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Soumis (En attente)'
        AI_EVALUATED = 'AI_EVALUATED', 'Évalué par SmartSujet (IA)'
        ADMIN_VALIDATED = 'ADMIN_VALIDATED', "Validé par l'Administration"
        ASSIGNED = 'ASSIGNED', 'Assigné à un Encadrant'
        REJECTED = 'REJECTED', 'Refusé'

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_subjects')
    title = models.CharField(max_length=255, verbose_name="Titre du sujet")
    abstract = models.TextField(verbose_name="Résumé descriptif & Impact sociétal (Abstract)")
    architecture_details = models.TextField(null=True, blank=True, verbose_name="Architecture du domaine & Base de données")
    time_feasibility = models.CharField(max_length=100, null=True, blank=True, verbose_name="Faisabilité dans le temps")
  
  
    keywords = models.CharField(max_length=255, help_text="Mots-clés techniques séparés par des virgules")


    ai_score = models.IntegerField(null=True, blank=True, verbose_name="Score d'acceptabilité IA (%)")
    ai_strengths = models.TextField(null=True, blank=True, verbose_name="Points forts & Faisabilité")
    ai_alerts = models.TextField(null=True, blank=True, verbose_name="Alertes & Risques")
    
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.SUBMITTED)
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='assigned_subjects', limit_choices_to={'role': 'SUPERVISOR'}
    )
    admin_comment = models.TextField(null=True, blank=True, verbose_name="Motif de refus ou commentaire admin")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
    
        if self.status in ['SUBMITTED', 'AI_EVALUATED']:
            existing_active = Subject.objects.filter(
                student=self.student,
                status__in=['ADMIN_VALIDATED', 'ASSIGNED']
            ).exclude(pk=self.pk).exists()
            
            if existing_active:
                raise ValidationError("Vous possédez déjà un sujet validé ou assigné par l'administration. Impossible de soumettre une nouvelle proposition.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.student.get_full_name() or self.student.username}"

class Project(models.Model):
    subject = models.OneToOneField(Subject, on_delete=models.PROTECT, related_name='project')
    student = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='active_project')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='supervised_projects')
    status = models.CharField(max_length=50, default='IN_PROGRESS', verbose_name="Statut du projet")
    final_grade = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Note finale")
    
    def __str__(self):
        return f"PFE: {self.subject.title}"

class Milestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255, verbose_name="Titre du jalon")
    description = models.TextField(null=True, blank=True)
    due_date = models.DateField(verbose_name="Date limite")
    is_validated = models.BooleanField(default=False, verbose_name="Validé par l'encadrant")

class Report(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    file = models.FileField(upload_to='reports/', verbose_name="Fichier PDF ou Word (.pdf, .doc, .docx)")
    description = models.TextField(null=True, blank=True, verbose_name="Description de l'envoi")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    supervisor_comment = models.TextField(null=True, blank=True, verbose_name="Commentaire de l'encadrant")
    is_reviewed = models.BooleanField(default=False, verbose_name="Traité / Archivé")
    is_vectorized = models.BooleanField(default=False, verbose_name="Indexé par le RAG")

    def __str__(self):
        return f"Rapport #ID-{self.id} - {self.project.student.username}"

class GroupMessage(models.Model):
    
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
        related_name='academic_group_chats', limit_choices_to={'role': 'SUPERVISOR'}
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_academic_messages')
    content = models.TextField(verbose_name="Contenu du message")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.sender.username} dans le groupe de {self.supervisor.username}"


auditlog.register(Subject)
auditlog.register(Project)
auditlog.register(Milestone)
auditlog.register(Report)
auditlog.register(GroupMessage)