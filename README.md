
# 🎓 ThesisPulse — Plateforme Intelligente de Gestion PFE & Soutenances

<div align="center">

![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0+-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![OR-Tools](https://img.shields.io/badge/Google_OR_Tools-Optimization-orange?style=for-the-badge)

*Une solution moderne, automatisée et intelligente pour la gestion, l'évaluation et la planification des Projets de Fin d'Études (PFE) universitaires.*

</div>

---

## 📌 Sommaire
1. [À Propos du Projet](#-à-propos-du-projet)
2. [Architecture & Stack Technique](#-architecture--stack-technique)
3. [Modules & Fonctionnalités Clés](#-modules--fonctionnalités-clés)
4. [Logique & Algorithmes Avancés](#-logique--algorithmes-avancés)
5. [Structure du Projet](#-structure-du-projet)
6. [Guide d'Installation & Docker](#-guide-dinstallation--docker)
7. [Auteure](#-auteure)

---

## 🚀 À Propos du Projet

**ThesisPulse** est une plateforme web universitaire de niveau production conçue pour numériser et fluidifier l'ensemble du cycle de vie des Projets de Fin d'Études (PFE). Elle résout les problématiques majeures des départements académiques : la surcharge administrative, le matching imprécis entre étudiants et encadrants, la lecture chronophage des rapports intermédiaires et les conflits de planification des soutenances.

Dotée d'une interface moderne au design **Glassmorphism**, la plateforme intègre l'intelligence artificielle (système RAG pour l'analyse documentaire) et la recherche opérationnelle (solveur d'optimisation de contraintes Google OR-Tools).

---

## ⚙️ Stack Technique

* **Backend :** Django 4.2+ (Python 3.11)
* **Frontend :** Tailwind CSS, HTML5, JavaScript moderne, HTMX
* **Base de données & Cache :** PostgreSQL 15, Redis
* **Tâches Asynchrones :** Celery
* **IA & Traitement Documentaire :** PyMuPDF (fitz), python-docx, Moteur RAG personnalisé
* **Optimisation & OR :** Google OR-Tools (CP-SAT Solver)
* **Conteneurisation :** Docker & Docker Compose

---

## 🧩 Modules & Fonctionnalités Clés

1. **Espace Administrateur / Coordinateur :**
   * Tableau de bord global avec statistiques en temps réel.
   * Génération automatique et propre des identifiants et e-mails professionnels (sans caractères superflus).
   * Lancement du solveur Google OR-Tools pour planifier automatiquement les soutenances.
   * Gestion du calendrier global et des événements institutionnels.

2. **Espace Étudiant (SmartSujet & Dépôt) :**
   * Soumission de sujets de PFE avec calcul d'affinité instantané avec les encadrants.
   * Dépôt de rapports intermédiaires au format PDF ou Word (`.docx`).
   * Suivi des retours et commentaires de l'encadrant rattachés par identifiant d'envoi (`#ID`).

3. **Espace Encadrant & Assistant RAG (Sidebar à 5 rubriques) :**
   * **Home :** Compteurs d'étudiants assignés, projets actifs et liste détaillée des étudiants.
   * **Projets & Boîte RAG :** Flux de réception style e-mail des rapports étudiants. Chaque message est accompagné d'un **Mini-Chatbot RAG** qui lit le document à la place de l'encadrant et répond aux questions ciblées. Une fois le commentaire soumis, le rapport disparaît de la file d'attente pour faire remonter le suivant.
   * **Groupe WhatsApp Interne :** Salon de discussion en temps réel entre l'encadrant et l'ensemble de ses étudiants supervisés.
   * **Espace Jury :** Module verrouillé par défaut, se débloquant automatiquement dès l'affectation par l'administration (affichage des salles, dates, heures et PV de soutenance).
   * **Profil :** Gestion des informations personnelles et des spécialités multiples.

---

## 🧠 Logique & Algorithmes Avancés

* **Algorithme de Matching d'Affinité :** Croise les spécialités multiples de l'encadrant (stockées en format JSON) avec les mots-clés, l'architecture et l'intitulé du sujet PFE de l'étudiant pour attribuer un score de compatibilité réaliste.
* **Moteur RAG Hybride (PDF & Word) :** Extrait automatiquement le texte brut des documents attachés aux rapports (`.pdf`, `.docx`), permet d'interroger le contenu sémantiquement et génère des ébauches de commentaires d'évaluation pour l'encadrant.
* **Optimisation des Soutenances (Google OR-Tools) :** Modélise le problème d'affectation des salles, des créneaux horaires et de la composition des jurys sous forme de satisfaction de contraintes (CP-SAT), garantissant zéro conflit d'horaire pour les enseignants.

---

## 📁 Structure du Projet

```text
ThesisPulse/
│
├── apps/
│   ├── academic/          # Modèles de sujets, projets, rapports et messages de groupe
│   ├── ai_module/         # Moteur RAG, matching d'affinité, tâches Celery et vues IA
│   ├── authentication/    # Modèle utilisateur personnalisé (Rôles, Filières, Spécialités)
│   └── scheduling/        # Gestion des salles, événements et solveur Google OR-Tools
│
├── templates/
│   ├── ai_dashboard/      # Templates du dashboard encadrant et mini-chatbot
│   ├── scheduling/        # Templates d'administration et plannings
│   └── base.html          # Template global avec conditions dynamiques pour les dashboards
│
├── docker-compose.yml     # Configuration multi-conteneurs (Web, DB, Redis)
├── Dockerfile             # Image de l'application Django & dépendances Python
├── manage.py              # Point d'entrée de gestion Django
└── requirements.txt       # Bibliothèques Python requises (incluant python-docx et PyMuPDF)

🐳 Guide d'Installation & Déploiement (Docker)
Prérequis
Docker et Docker Compose installés sur votre machine.

Étapes de lancement :
Cloner le dépôt :

Bash
git clone [https://github.com/ton-pseudo/ThesisPulse.git](https://github.com/ton-pseudo/ThesisPulse.git)
cd ThesisPulse
Lancer les conteneurs avec Docker Compose :

Bash
docker-compose up --build -d
Appliquer les migrations de base de données :

Bash
docker exec -it thesis_pulse_web python manage.py migrate
Créer un compte administrateur :

Bash
docker exec -it thesis_pulse_web python manage.py createsuperuser
Accéder à l'application :
Ouvrez votre navigateur à l'adresse : http://127.0.0.1:8000
