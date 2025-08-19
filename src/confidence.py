from src.models import ExtractedField, QualityAssurance

def score_confidence(field: ExtractedField) -> float:
    if not field.value or field.value == "NOT_FOUND":
        return 0.0
    if len(field.value) > 3:
        return 0.7
    return 0.5

def aggregate_confidence(fields, qa: QualityAssurance) -> float:
    base = sum(f.confidence for f in fields) / max(len(fields), 1)
    penalty = 0.1 * len(qa.failed_rules)
    bonus = 0.05 * len(qa.passed_rules)
    score = base + bonus - penalty
    return max(0, min(score, 1))

def validate_fields(fields, doc_type) -> QualityAssurance:
    # Example: Check required fields (very naïve implementation)
    passed = []
    failed = []
    notes = []
    required = {
        "invoice": ["invoice_number","total_amount"],
        "medical_bill": ["patient_name","provider_name"],
        "prescription": ["patient_name","prescriber_name"]
    }.get(doc_type, [])
    found = {f.name for f in fields}
    for req in required:
        if req in found:
            passed.append(f"{req}_present")
        else:
            failed.append(f"{req}_missing")
    return QualityAssurance(passed_rules=passed, failed_rules=failed, notes="; ".join(failed))
