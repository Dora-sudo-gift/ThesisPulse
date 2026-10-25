from django.contrib.auth.models import AbstractUser
from django.db import models
import random

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Étudiant'
        SUPERVISOR = 'SUPERVISOR', 'Encadrant / Enseignant'
        ADMIN = 'ADMIN', 'Administration / Coordinateur'
        JURY = 'JURY', 'Membre du Jury'

    
    class Filiere(models.TextChoices):
        SEN = 'SEN', 'SEN - Software Engineering (Génie Logiciel)'
        CYS = 'CYS', 'CYS - Cybersecurity (Cybersécurité)'
        CS = 'CS', 'CS - Computer Science (Informatique Fondamentale)'
        DS = 'DS', 'DS - Data Science & Big Data'
        AI = 'AI', 'AI - Intelligence Artificielle & Machine Learning'
        NET = 'NET', 'NET - Réseaux & Télécommunications'
        CLOUD = 'CLOUD', 'CLOUD - Cloud Computing & Virtualisation'
        IOT = 'IOT', 'IOT - Internet des Objets & Systèmes Embarqués'
        IS = 'IS', 'IS - Systèmes d\'Information & ERP'
        DEVOPS = 'DEVOPS', 'DEVOPS - Ingénierie DevOps & Automatisation'
        WEB = 'WEB', 'WEB - Développement Web & Mobile Avancé'
        BIO = 'BIO', 'BIO - Bio-informatique & Santé Numérique'

    
    class Specialite(models.TextChoices):
        DEVOPS = 'DEVOPS', 'DevOps & CI/CD'
        MICROSERVICES = 'MICROSERVICES', 'Architecture Microservices & Docker'
        FRONTEND = 'FRONTEND', 'Développement Frontend (React, Vue, Tailwind)'
        BACKEND = 'BACKEND', 'Développement Backend (Django, FastAPI, Node.js)'
        PYTHON = 'PYTHON', 'Écosystème Python Avancé'
        PENTEST = 'PENTEST', 'Cybersécurité Offensive & Pentesting (Kali, Metasploit)'
        NETSEC = 'NETSEC', 'Sécurité Réseau, IDS/IPS & Wireshark'
        NLP_RAG = 'NLP_RAG', 'Traitement du Langage Naturel (NLP) & Systèmes RAG'
        ML_DL = 'ML_DL', 'Machine Learning & Deep Learning'
        CLOUD_ARCH = 'CLOUD_ARCH', 'Architecture Cloud (AWS, Azure, GCP)'
        BLOCKCHAIN = 'BLOCKCHAIN', 'Blockchain, Smart Contracts & Web3'
        BIGDATA = 'BIGDATA', 'Big Data, Apache Spark & Kafka'
        MOBILE = 'MOBILE', 'Développement Mobile (Flutter, React Native)'
        IOT_EMB = 'IOT_EMB', 'IoT, Arduino, Raspberry Pi & Systèmes Embarqués'
        DB_ADMIN = 'DB_ADMIN', 'Bases de Données Relationnelles, NoSQL & pgvector'
        AUDIT_SI = 'AUDIT_SI', 'Audit des Systèmes d\'Information & Gouvernance IT'
        ERP_SAP = 'ERP_SAP', 'Intégration ERP (Odoo, SAP)'
        CRYPTO = 'CRYPTO', 'Cryptographie Appliquée & Sécurité des Données'
        SYS_LINUX = 'SYS_LINUX', 'Administration Systèmes Linux & Bash'
        ALGO_OPT = 'ALGO_OPT', 'Algorithmique, Recherche Opérationnelle & OR-Tools'
        QA_TEST = 'QA_TEST', 'Qualité Logicielle, Tests Automatisés & TDD'
        UI_UX = 'UI_UX', 'Conception UI/UX & Ergonomie Web'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name="Rôle principal"
    )
    
    is_jury_member = models.BooleanField(
        default=False,
        verbose_name="Membre du jury habilité"
    )
    
    
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Âge")
    quartier = models.CharField(max_length=150, null=True, blank=True, verbose_name="Quartier de résidence")
    phone_number = models.CharField(max_length=30, null=True, blank=True, verbose_name="Numéro de téléphone")
    
    
    matricule = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True, 
        verbose_name="Matricule Universitaire"
    )
    
    
    filiere = models.CharField(
        max_length=30,
        choices=Filiere.choices,
        null=True,
        blank=True,
        verbose_name="Filière (Étudiant)"
    )
    specialites = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Spécialités (Encadrant)"
    )
    
    
    department = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        verbose_name="Département / Filière"
    )

    
    visible_password = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name="Mot de passe visible (Admin)"
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        if self.role == self.Role.STUDENT and not self.matricule:
            while True:
                new_mat = f"ICTU2026{random.randint(10, 9999)}"
                if not User.objects.filter(matricule=new_mat).exists():
                    self.matricule = new_mat
                    break
        
        if self.role == self.Role.STUDENT and self.filiere:
            self.department = str(self.get_filiere_display())[:255]
        elif self.role == self.Role.SUPERVISOR and self.specialites:
            joined_specs = ", ".join(self.specialites) if isinstance(self.specialites, list) else str(self.specialites)
            self.department = joined_specs[:255]

    
        super().save(*args, **kwargs)

    def __str__(self):
        full = f"{self.first_name} {self.last_name}".strip() or self.username
        return f"{full} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_supervisor(self):
        return self.role == self.Role.SUPERVISOR or self.is_jury_member

    @property
    def is_coordinator(self):
        return self.role == self.Role.ADMIN

    @property
    def is_jury(self):
        return self.role == self.Role.JURY or self.is_jury_member


class PasswordResetRequest(models.Model):
    email = models.EmailField(verbose_name="Email demandé")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="reset_requests")
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False, verbose_name="Traité par l'admin")

    def __str__(self):
        return f"Demande de {self.email} - {'Traité' if self.is_resolved else 'En attente'}"