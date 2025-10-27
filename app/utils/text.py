import unicodedata

def normalize_key(s: str | None) -> str | None:
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    return unicodedata.normalize("NFKC", s).casefold()
