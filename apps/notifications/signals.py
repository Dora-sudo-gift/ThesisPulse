from auditlog.models import LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.academic.models import Subject, Project
from .models import Notification

@receiver(post_save, sender=Subject)
def notify_subject_status_change(sender, instance, created, **kwargs):
    
    if not created:
        Notification.objects.create(
            user=instance.student,
            title="Mise à jour de votre sujet",
            message=f"Le statut de votre sujet '{instance.title}' est passé à : {instance.get_status_display()}"
        )