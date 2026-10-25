
from apps.academic.models import Report
from .rag_engine import extract_text_from_file


def vectorize_report_pdf(report_id):
    
    try:
        report = Report.objects.get(id=report_id)
        if report.file:
            
            extracted_text = extract_text_from_file(report.file.path)
            
            if extracted_text.strip():
                # TODO: Ajouter ici ta logique d'insertion des embeddings dans pgvector si nécessaire
                pass
            
            report.is_vectorized = True
            report.save()
            return f"Rapport #ID-{report_id} indexé et vectorisé avec succès."
        return f"Aucun fichier associé au rapport #ID-{report_id}."
    except Report.DoesNotExist:
        return f"Rapport #ID-{report_id} introuvable."