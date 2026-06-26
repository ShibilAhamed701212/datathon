def transcribe_audio(audio_data: bytes = None) -> str:
    try:
        from openai import OpenAI
        import tempfile
        import os
        if not audio_data:
            return "Placeholder: Audio transcription would process here. Try asking about theft cases in Bengaluru."
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.write(audio_data)
        tmp.close()
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with open(tmp.name, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        os.unlink(tmp.name)
        return transcript.text
    except ImportError:
        return "Whisper transcription not available. Voice input is a placeholder in this demo."
    except Exception as e:
        return f"Transcription error: {str(e)}"
