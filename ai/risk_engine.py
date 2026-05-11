from typing import Dict, Any


def assess_risk(assessment_data: Dict[str, Any]) -> Dict[str, Any]:
    risk_score = 0
    reasons = []

    pain_severity = assessment_data.get("pain_severity", 0)
    if pain_severity is not None:
        try:
            pain_severity = int(pain_severity)
        except (ValueError, TypeError):
            pain_severity = 0
    else:
        pain_severity = 0

    numbness = str(assessment_data.get("numbness", "")).lower()
    muscle_weakness = str(assessment_data.get("muscle_weakness", "")).lower()
    nerve_radiation = str(assessment_data.get("nerve_radiation", "")).lower()
    sleep_disturbance = str(assessment_data.get("sleep_disturbance", "")).lower()
    prev_surgery = str(assessment_data.get("previous_spine_surgery", "")).lower()

    if pain_severity >= 8 and numbness == "yes":
        risk_score += 3
        reasons.append("Severe pain with numbness")
    if pain_severity >= 7 and nerve_radiation == "yes":
        risk_score += 2
        reasons.append("High pain with nerve radiation")
    if muscle_weakness == "yes":
        risk_score += 2
        reasons.append("Muscle weakness present")
    if numbness == "yes" and nerve_radiation == "yes":
        risk_score += 2
        reasons.append("Numbness with nerve radiation")
    if prev_surgery and "yes" in prev_surgery:
        risk_score += 1
        reasons.append("Previous spine surgery")
    if pain_severity >= 6 and sleep_disturbance == "yes":
        risk_score += 1
        reasons.append("Pain affecting sleep")
    if pain_severity <= 3:
        risk_score = max(0, risk_score - 1)

    risk_level = "LOW"
    if risk_score >= 6:
        risk_level = "CRITICAL"
    elif risk_score >= 4:
        risk_level = "HIGH"
    elif risk_score >= 2:
        risk_level = "MODERATE"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "reasons": reasons,
        "surgery_probability": "HIGH" if risk_score >= 5 else "MODERATE" if risk_score >= 3 else "LOW",
    }
