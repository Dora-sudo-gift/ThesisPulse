from django.db import models
from django.conf import settings

class Room(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la salle")
    capacity = models.IntegerField(default=30, verbose_name="Capacité d'accueil")
    is_available = models.BooleanField(default=True, verbose_name="Disponible pour les soutenances")

    def __str__(self):
        return f"{self.name} (Capacité : {self.capacity} places)"

class Event(models.Model):
    
    title = models.CharField(max_length=255, verbose_name="Titre de l'événement")
    description = models.TextField(null=True, blank=True, verbose_name="Détails")
    date = models.DateTimeField(verbose_name="Date et heure de l'événement")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%d/%m/%Y %H:%M')})"

class GroupMessage(models.Model):
    
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
        related_name='scheduling_group_chats', limit_choices_to={'role': 'SUPERVISOR'},
        verbose_name="Encadrant responsable du groupe"
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Auteur du message")
    message = models.TextField(verbose_name="Message")
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.sent_at.strftime('%H:%M')}] {self.sender.get_full_name()}: {self.message[:30]}"

class DefenseSchedule(models.Model):
    
    project = models.OneToOneField('academic.Project', on_delete=models.CASCADE, related_name='defense_slot', verbose_name="Projet PFE")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Salle assignée")
    defense_date = models.DateTimeField(verbose_name="Date et heure de soutenance")
    jury_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='jury_defenses', blank=True, verbose_name="Membres du jury assignés")
    is_published = models.BooleanField(default=True, verbose_name="Planning publié et actif")

    def __str__(self):
        return f"Soutenance de {self.project.student.username} en {self.room.name if self.room else 'Salle TBD'} le {self.defense_date.strftime('%d/%m/%Y %H:%M')}"