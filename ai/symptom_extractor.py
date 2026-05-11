

PAIN_KEYWORDS = [
    "pain", "ache", "hurt", "stiff", "numb", "tingling", "burning",
    "shooting", "throbbing", "cramp", "spasm", "swelling", "tenderness",
    "weakness", "radiation", "pulling", "tightness", "pressure",
]

BODY_PARTS = [
    "neck", "shoulder", "back", "spine", "leg", "arm", "hand",
    "foot", "hip", "knee", "elbow", "wrist", "ankle", "head",
    "cervical", "lumbar", "thoracic", "sacrum", "pelvis",
    "finger", "toe", "thigh", "calf", "heel", "rib",
]


def extract_symptoms(transcript: str) -> dict:
    if not transcript:
        return {"pain_keywords": [], "body_parts": [], "symptom_count": 0}

    text = transcript.lower()

    found_keywords = [kw for kw in PAIN_KEYWORDS if kw in text]
    found_body_parts = [bp for bp in BODY_PARTS if bp in text]

    return {
        "pain_keywords": found_keywords,
        "body_parts": found_body_parts,
        "symptom_count": len(found_keywords) + len(found_body_parts),
    }
