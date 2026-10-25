from ortools.sat.python import cp_model
from django.utils import timezone
from datetime import timedelta
from apps.scheduling.models import Room, DefenseSchedule
from apps.academic.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_defense_schedule():
    
    model = cp_model.CpModel()
    
    
    projects = list(Project.objects.filter(status='IN_PROGRESS').select_related('student', 'supervisor', 'subject'))
    rooms = list(Room.objects.filter(is_available=True))
    supervisors = list(User.objects.filter(role='SUPERVISOR'))
    
    if not projects:
        raise ValueError("Aucun projet actif trouvé pour la planification des soutenances.")
    if not rooms:
        raise ValueError("Aucune salle n'est disponible pour les soutenances. Veuillez en ajouter.")

    num_projects = len(projects)
    num_rooms = len(rooms)
    
    print(f"--- Google OR-Tools : Lancement de l'optimisation ---")
    print(f"Nombre de projets à planifier : {num_projects}")
    print(f"Nombre de salles disponibles : {num_rooms}")

    base_time = timezone.now() + timedelta(days=2)
    base_time = base_time.replace(hour=9, minute=0, second=0, microsecond=0)
    
    slots_per_day = 6  
    total_slots = max(num_projects, slots_per_day)

    
    x = {}
    for p_idx in range(num_projects):
        for r_idx in range(num_rooms):
            for s_idx in range(total_slots):
                x[(p_idx, r_idx, s_idx)] = model.NewBoolVar(f'proj_{p_idx}_room_{r_idx}_slot_{s_idx}')

    
    for p_idx in range(num_projects):
        model.Add(
            sum(x[(p_idx, r_idx, s_idx)] for r_idx in range(num_rooms) for s_idx in range(total_slots)) == 1
        )

    
    for r_idx in range(num_rooms):
        for s_idx in range(total_slots):
            model.Add(
                sum(x[(p_idx, r_idx, s_idx)] for p_idx in range(num_projects)) <= 1
            )

    
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("--- Planification OR-Tools réussie avec succès ---")
        
        
        DefenseSchedule.objects.all().delete()

        for p_idx, project in enumerate(projects):
            assigned_room = rooms[0]
            assigned_slot = p_idx
            
            for r_idx in range(num_rooms):
                for s_idx in range(total_slots):
                    if solver.Value(x[(p_idx, r_idx, s_idx)]) == 1:
                        assigned_room = rooms[r_idx]
                        assigned_slot = s_idx
                        break

            day_offset = assigned_slot // slots_per_day
            hour_offset = (assigned_slot % slots_per_day)
            defense_datetime = base_time + timedelta(days=day_offset, hours=hour_offset)

            
            defense_slot = DefenseSchedule.objects.create(
                project=project,
                room=assigned_room,
                defense_date=defense_datetime,
                is_published=True
            )

            
            primary_supervisor = project.supervisor
            if primary_supervisor:
                defense_slot.jury_members.add(primary_supervisor)
                primary_supervisor.is_jury_member = True
                primary_supervisor.save()

            
            other_supervisors = [sup for sup in supervisors if sup != primary_supervisor]
            if other_supervisors:
                subject_text = f"{project.subject.title} {project.subject.abstract} {project.student.filiere}".lower()
                
                best_sup = other_supervisors[0]
                best_score = -1
                for sup in other_supervisors:
                    sup_specs = getattr(sup, 'specialites', [])
                    if isinstance(sup_specs, str):
                        sup_specs = [s.strip() for s in sup_specs.split(',') if s.strip()]
                    score = sum(1 for spec in sup_specs if any(word in subject_text for word in spec.lower().split() if len(word) > 2))
                    if score > best_score:
                        best_score = score
                        best_sup = sup

                second_jury = best_sup
                defense_slot.jury_members.add(second_jury)
                second_jury.is_jury_member = True
                second_jury.save()

        return True
    else:
        raise RuntimeError("Le solveur OR-Tools n'a pas pu trouver de solution optimale pour les contraintes actuelles.")