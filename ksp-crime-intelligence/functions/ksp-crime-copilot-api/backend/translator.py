from typing import Optional

_translator = None

def _get_translator():
    global _translator
    if _translator is None:
        try:
            from deep_translator import GoogleTranslator
            _translator = GoogleTranslator
        except ImportError:
            try:
                from googletrans import Translator
                _translator = Translator()
            except ImportError:
                _translator = None
    return _translator

def translate_to_english(text: str, source: str = "kn") -> str:
    if not text or source == "en":
        return text
    try:
        tr = _get_translator()
        if tr is None:
            return f"[{text}] (translation unavailable)"
        if hasattr(tr, 'translate'):
            return tr(source=source, target='en').translate(text)
        from googletrans import Translator
        t = Translator()
        return t.translate(text, src=source, dest='en').text
    except Exception as e:
        return f"[{text}] (translation error: {e})"

def translate_to_kannada(text: str) -> str:
    if not text:
        return text
    try:
        tr = _get_translator()
        if tr is None:
            return f"[{text}] (translation unavailable)"
        if hasattr(tr, 'translate'):
            return tr(source='en', target='kn').translate(text)
        from googletrans import Translator
        t = Translator()
        return t.translate(text, src='en', dest='kn').text
    except Exception as e:
        return f"[{text}] (translation error: {e})"
