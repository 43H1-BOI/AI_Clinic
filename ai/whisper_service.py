from faster_whisper import WhisperModel

_model = None


def get_whisper_model():
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def transcribe_audio(audio_path: str) -> dict:
    try:
        model = get_whisper_model()
        segments, info = model.transcribe(audio_path, language=None, beam_size=5)

        detected_language = info.language if info else "unknown"
        segments_list = list(segments)
        full_text = " ".join((seg.text or "").strip() for seg in segments_list)

        return {
            "success": True,
            "transcript": full_text,
            "language": detected_language,
            "segments": [
                {"start": seg.start, "end": seg.end, "text": (seg.text or "").strip()}
                for seg in segments_list
            ],
        }
    except Exception as e:
        return {
            "success": False,
            "transcript": "",
            "language": "unknown",
            "error": str(e),
        }
