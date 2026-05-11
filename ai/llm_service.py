import json
import os
from openai import OpenAI
from ai.prompts import AI_ANALYSIS_SYSTEM_PROMPT, AI_ANALYSIS_USER_PROMPT
from database.schema import AIAnalysisOutput

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            _client = OpenAI(api_key=api_key)
    return _client


def analyze_with_llm(transcript: str, patient_info: str = "", consultation_notes: str = "", assessment_data: str = "", max_retries: int = 2) -> dict:
    client = get_client()
    if not client:
        return {"error": "OpenAI API key not configured", "fallback": True}

    prompt = AI_ANALYSIS_USER_PROMPT.format(
        patient_info=patient_info,
        transcript=transcript[:4000],
        consultation_notes=consultation_notes[:2000],
        assessment_data=assessment_data[:2000],
    )

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": AI_ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            content = (response.choices[0].message.content or "").strip()
            parsed = json.loads(content)
            validated = AIAnalysisOutput(**parsed)
            return validated.model_dump()
        except Exception as e:
            if attempt < max_retries:
                continue
            return {"error": str(e), "fallback": True}

    return {"error": "Max retries exceeded", "fallback": True}
