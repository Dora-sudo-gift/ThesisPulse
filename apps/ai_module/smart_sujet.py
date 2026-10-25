import re

def evaluate_subject_abstract(abstract, keywords, title="", architecture_details="", time_feasibility=""):
    
    abstract_clean = (abstract or "").strip()
    arch_clean = (architecture_details or "").strip()
    title_clean = (title or "").strip()
    keywords_clean = (keywords or "").strip()
    time_clean = (time_feasibility or "").strip()

    full_text = f"{title_clean} {abstract_clean} {arch_clean}".lower()
    words = re.findall(r'\b\w+\b', full_text)
    word_count = len(words)

    
    if word_count < 15 or len(abstract_clean) < 50:
        return {
            'score': max(8, min(22, word_count)),
            'strengths': "Proposition trop succincte pour valider une architecture PFE.",
            'alerts': (
                "❌ Longueur critique : Votre description ne détaille ni l'architecture du domaine, "
                "ni la structure de la base de données, ni l'impact sociétal réel."
            )
        }

    strengths = []
    alerts = []

    feasibility_score = 0.0

    scope_terms = [
        'mvp', 'prototype', 'module', 'phase', 'jalon', 'sprint', 'agile', 'scrum',
        'périmètre', 'livrable', 'étape', 'déploiement', 'test', 'validation', 'contrainte',
        'délai', 'planning', 'fonctionnalité', 'cahier des charges'
    ]
    found_scope = [t for t in scope_terms if t in full_text]
    feasibility_score += min(10.0, len(found_scope) * 2.5)

    if time_clean:
        feasibility_score += 5.0

    heavy_tech_terms = [
        'blockchain', 'smart contract', 'deep learning', 'llm', 'rag', 'microservice',
        'kubernetes', 'iot', 'embarqué', 'temps réel', 'big data', 'spark', 'kafka',
        'cryptographie', 'pentesting', 'distribué', 'cloud native'
    ]
    found_heavy_tech = [t for t in heavy_tech_terms if t in full_text or t in keywords_clean.lower()]

    if len(found_heavy_tech) > 4 and ("3 mois" in time_clean.lower() or word_count < 55):
        feasibility_score += 2.0
        alerts.append(
            f"⚠️ Risque de faisabilité temporelle : Vous combinez trop de technologies lourdes ({', '.join(found_heavy_tech[:4])}) "
            "pour un délai court sans découpage modulaire (MVP) précis."
        )
    elif 1 <= len(found_heavy_tech) <= 4:
        feasibility_score += 10.0
        strengths.append(
            f"⏱️ Faisabilité temporelle cohérente : Périmètre technique réaliste et réalisable dans les délais ({time_clean or '4 à 6 mois'})."
        )
    else:
        feasibility_score += 6.0

    feasibility_score = min(25.0, feasibility_score)

    arch_score = 0.0

    arch_patterns = [
        'architecture', 'microservice', 'monolithique', 'mvc', 'mvvm', 'mvt', 'rest', 'api',
        'graphql', 'websocket', 'docker', 'conteneur', 'ci/cd', 'pipeline', 'nginx', 'gateway',
        'orchestration', 'client-serveur', 'tiers', 'couche', 'backend', 'frontend', 'rag',
        'vector', 'sécurité', 'authentification', 'jwt', 'oauth', 'chiffrement', 'tls',
        'pare-feu', 'ids', 'ips', 'modèle', 'algorithme', 'or-tools', 'solveur'
    ]
    found_arch = [t for t in arch_patterns if t in full_text or t in keywords_clean.lower()]

    arch_score += min(16.0, len(found_arch) * 2.7)

    if len(arch_clean) >= 60:
        arch_score += 6.0
    elif len(arch_clean) >= 25:
        arch_score += 3.0

    kw_list = [k.strip() for k in re.split(r'[,;/]+', keywords_clean) if k.strip()]
    if len(kw_list) >= 3:
        arch_score += 3.0
    else:
        alerts.append("⚠️ Stack technique floue : Précisez au moins 3 à 4 technologies ou protocoles dans les mots-clés.")

    arch_score = min(25.0, arch_score)

    if arch_score >= 16:
        strengths.append(f"🏗️ Bonne maîtrise de l'architecture du domaine ({', '.join(found_arch[:5])}).")
    else:
        alerts.append("⚠️ Architecture du domaine incomplète : Explicitez comment communiquent vos composants (API, couches, sécurité, flux).")

    db_score = 0.0

    db_engines = [
        'postgresql', 'postgres', 'mysql', 'mariadb', 'mongodb', 'nosql', 'redis',
        'sqlite', 'oracle', 'sql server', 'cassandra', 'elasticsearch', 'pgvector',
        'neo4j', 'firebase', 'supabase', 'timescaledb', 'chromadb'
    ]
    db_concepts = [
        'base de données', 'schéma', 'modélisation', 'uml', 'merise', 'mcd', 'mld',
        'entité', 'table', 'relationnel', 'indexation', 'requête', 'transaction',
        'acid', 'migration', 'volumétrie', 'stockage', 'intégrité', 'normalisation',
        'collecte', 'dataset', 'données', 'historisation', 'sauvegarde', 'orm'
    ]

    found_db_engines = [e for e in db_engines if e in full_text or e in keywords_clean.lower()]
    found_db_concepts = [c for c in db_concepts if c in full_text]

    if found_db_engines:
        db_score += min(11.0, len(found_db_engines) * 5.5)
    if found_db_concepts:
        db_score += min(14.0, len(found_db_concepts) * 2.8)

    db_score = min(25.0, db_score)

    if db_score >= 15:
        db_details = found_db_engines + found_db_concepts[:3]
        strengths.append(f"🗄️ Structure de données pertinente et bien identifiée ({', '.join(db_details)}).")
    elif db_score >= 8:
        alerts.append("⚠️ Base de données partiellement décrite : Précisez le SGBD exact (ex: PostgreSQL, MongoDB) et la volumétrie ou modélisation (UML/MCD).")
    else:
        alerts.append("❌ Absence de stratégie de données : Aucun SGBD ni modèle de stockage n'est clairement mentionné.")

    society_score = 0.0

    problem_indicators = [
        'problème', 'problématique', 'défi', 'difficulté', 'manque', 'lenteur',
        'erreur', 'perte', 'fraude', 'insécurité', 'conflit', 'engorgement',
        'coût', 'risque', 'pénurie', 'fracture', 'besoin', 'urgence', 'limite'
    ]
    impact_domains = [
        'société', 'social', 'citoyen', 'hôpital', 'santé', 'patient', 'médical',
        'université', 'académique', 'étudiant', 'éducation', 'école', 'entreprise',
        'cameroun', 'afrique', 'local', 'urbain', 'transport', 'agriculture', 'paysan',
        'énergie', 'banque', 'finance', 'commerce', 'administration', 'service public',
        'environnement', 'logistique', 'sécurité', 'communauté', 'utilisateur'
    ]
    solution_verbs = [
        'résoudre', 'optimiser', 'automatiser', 'fiabiliser', 'sécuriser', 'réduire',
        'améliorer', 'faciliter', 'accélérer', 'dématérialiser', 'prédire', 'prévenir'
    ]

    found_problems = [p for p in problem_indicators if p in full_text]
    found_domains = [d for d in impact_domains if d in full_text]
    found_solutions = [s for s in solution_verbs if s in full_text]

    society_score += min(8.0, len(found_problems) * 2.8)
    society_score += min(10.0, len(found_domains) * 3.2)
    society_score += min(7.0, len(found_solutions) * 2.5)

    society_score = min(25.0, society_score)

    if society_score >= 16:
        strengths.append(f"🌍 Fort impact sociétal : Le projet répond à un problème réel et concret ({', '.join(found_domains[:3])}).")
    else:
        alerts.append("⚠️ Impact sociétal peu explicite : Montrez clairement quel problème réel de la société ou des entreprises votre solution résout.")

    
    penalty = 0.0
    bonus = 0.0

    ai_cliches = [
        'dans un monde en constante évolution', 'à l\'ère du numérique', 'révolutionner le secteur',
        'force est de constater', 'joue un rôle crucial', 'synergie', 'holistique',
        'paradigme', 'incontournable', 'de nos jours', 'transformation digitale globale'
    ]
    found_cliches = [c for c in ai_cliches if c in full_text]
    if found_cliches and (arch_score < 12 or db_score < 10):
        penalty += len(found_cliches) * 4.5
        alerts.append(
            "🤖 Alerte Formulation IA Générique : Votre texte contient des formules creuses typiques des IA "
            "au détriment des spécifications techniques et de la base de données."
        )

    trivial_topics = [
        'gestion de bibliothèque', 'gestion de stock', 'site vitrine', 'blog',
        'to-do list', 'calculatrice', 'gestion des notes', 'annuaire', 'catalogue simple'
    ]
    found_trivial = [t for t in trivial_topics if t in full_text]

    if found_trivial and len(found_cliches) == 0:
        penalty += 14.0
        alerts.append(
            f"❌ Sujet jugé trop basique ({found_trivial[0]}) : Pour un PFE, un simple système CRUD ne suffit pas. "
            "Intégrez de l'optimisation algorithmique, de l'IA, de la haute sécurité ou une architecture distribuée."
        )

    unique_words = set(words)
    lexical_diversity = len(unique_words) / float(word_count) if word_count > 0 else 0
    if word_count >= 65 and lexical_diversity >= 0.58:
        bonus += 3.5
    elif word_count < 35:
        penalty += 6.0
        alerts.append("⚠️ Description trop brève : Développez davantage vos arguments techniques et méthodologiques.")

    raw_score = feasibility_score + arch_score + db_score + society_score + bonus - penalty

    structural_hash = ((len(abstract_clean) * 3) + (len(arch_clean) * 7) + (len(kw_list) * 11)) % 5 - 2
    final_score = int(round(raw_score + (structural_hash * 0.6)))

    
    final_score = max(12, min(98, final_score))

    breakdown_summary = (
        f"[Détail IA — Faisabilité: {int(round(feasibility_score))}/25 | "
        f"Architecture: {int(round(arch_score))}/25 | "
        f"Base de données: {int(round(db_score))}/25 | "
        f"Impact Sociétal: {int(round(society_score))}/25]"
    )

    strengths_text = f"{breakdown_summary} " + (" ".join(strengths) if strengths else "Fondations techniques en cours d'analyse.")
    alerts_text = " ".join(alerts) if alerts else "✅ Aucune alerte majeure détectée. Sujet très solide, bien architecturé et prêt pour validation par l'Administration."

    return {
        'score': final_score,
        'strengths': strengths_text,
        'alerts': alerts_text
    }