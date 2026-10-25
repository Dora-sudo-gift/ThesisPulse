from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.scheduling.models import Room  # Assurez-vous que le modèle Room existe dans scheduling.models

User = get_user_model()

class Command(BaseCommand):
    help = "Initialise les données de référence (10 salles et 10 enseignants) pour l'établissement."

    def handle(self, *args, **kwargs):
        self.stdout.write("Début de l'initialisation des données de référence...")

        
        rooms_data = [
            "George mbarika",
            "pondi hall",
            "chumbo hall",
            "ericka hall",
            "french hall",
            "french hall 2",
            "cisko lab",
            "computer lab",
            "network hall",
            "optique hall"
        ]

        for r_name in rooms_data:
            room, created = Room.objects.get_or_create(name=r_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Salle créée : {r_name}"))
            else:
                self.stdout.write(f"La salle existe déjà : {r_name}")
        
        teachers_data = [
            {"username": "Engr. Tekoh Palma", "first_name": "Tekoh", "last_name": "palma", "email": "palma@tekohictuniversity.edu", "expertise": "django, python, api, microservices"},
            {"username": "Dr FOTSING KUETCHE", "first_name": "Fotsing", "last_name": "kuetche", "email": "Fotsing.fk@gmail.com", "expertise": "cybersecurity, kali, linux, network, wireshark"},
            {"username": "Engr ngomo", "first_name": "Christian", "last_name": "Ngomo", "email": "christian.ngomo@ictuniversity.edu", "expertise": "react, frontend, tailwind, ui, javascript"},
            {"username": "prof.mbarga", "first_name": "David", "last_name": "Mbarga", "email": "david.mbarga@ictuniversity.edu", "expertise": "postgresql, database, sql, data, optimization"},
            {"username": "ing.tientcheu", "first_name": "Evelyne", "last_name": "Tientcheu", "email": "evelyne.tientcheu@ictuniversity.edu", "expertise": "machine learning, nlp, ai, python, tensorflow"},
            {"username": "Engr. Daniel Moune", "first_name": "Moune", "last_name": "daniel", "email": "moune.daniel@ictuniversity.edu.cm", "expertise": "devops, docker, kubernetes, CI/CD, cloud"},
            {"username": "prof.mefo", "first_name": "Gisèle", "last_name": "Mefo", "email": "gisele.mefo@ictuniversity.edu", "expertise": "software engineering, uml, agile, scrum, management"},
            {"username": "ing.ngono", "first_name": "Hervé", "last_name": "Assi", "email": "herve.assi@ictuniversity.edu", "expertise": "compiler, python, parser, formal languages, grammar"},
            {"username": "prof.emilie", "first_name": "Inès", "last_name": "Kouam", "email": "ines.kouam@ictuniversity.edu", "expertise": "java, spring boot, enterprise, architecture, backend"},
            {"username": "Engr. Tanwi Nkiamboh", "first_name": "Nkiamboh", "last_name": "tawi", "email": "Nkiamboh.tanwi@ictuniversity.edu.cm", "expertise": "software, python"}
        ]

        for t_data in teachers_data:
            user, created = User.objects.get_or_create(
                username=t_data["username"],
                defaults={
                    "first_name": t_data["first_name"],
                    "last_name": t_data["last_name"],
                    "email": t_data["email"],
                    "is_staff": True, 
                }
            )
            if created:
                user.set_password("mses0610") 
                
                if hasattr(user, 'role'):
                    user.role = 'SUPERVISOR'
                if hasattr(user, 'expertise'):
                    user.expertise = t_data["expertise"]
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Enseignant créé : {user.get_full_name()} ({user.username}))"))
            else:
                self.stdout.write(f"L'enseignant existe déjà : {user.username}")

        self.stdout.write(self.style.SUCCESS("Initialisation des données terminée avec succès !"))