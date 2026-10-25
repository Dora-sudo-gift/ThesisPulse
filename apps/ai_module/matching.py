from django.contrib.auth import get_user_model

User = get_user_model()

def find_top_supervisors(subject):
    
    
    supervisors = User.objects.filter(role='SUPERVISOR')
    if not supervisors.exists():
        
        supervisors = User.objects.filter(is_staff=True)

    
    subject_text = f"{subject.title} {subject.abstract} {getattr(subject, 'architecture_details', '')} {subject.keywords}".lower()
    subject_keywords = [kw.strip().lower() for kw in subject.keywords.split(',') if kw.strip()]
    
    scored_supervisors = []
    
    for sup in supervisors:
        score = 25  
        
        # 3. Récupérer les spécialités de l'encadrant
        sup_specialites = getattr(sup, 'specialites', [])
        if isinstance(sup_specialites, str):
            sup_specialites = [s.strip() for s in sup_specialites.split(',') if s.strip()]
        
        sup_specialites_lower = [str(s).lower() for s in sup_specialites]
        
        
        matching_specs = 0
        for spec in sup_specialites_lower:
            spec_parts = spec.replace('&', ' ').split()
            if any(part in subject_text for part in spec_parts if len(part) > 2):
                matching_specs += 1
        
        score += matching_specs * 25


        common_matches = sum(1 for kw in subject_keywords if any(kw in spec for spec in sup_specialites_lower))
        score += common_matches * 15


        department = (getattr(sup, 'department', '') or '').lower()
        if department and any(word in subject_text for word in department.split() if len(word) > 3):
            score += 15

        
        final_score = max(15, min(98, score))
        
        scored_supervisors.append({
            'supervisor': sup,
            'affinity_score': final_score,
            'matched_specialties': sup_specialites
        })
    
    
    scored_supervisors.sort(key=lambda x: x['affinity_score'], reverse=True)
    return scored_supervisors[:5]