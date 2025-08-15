import re, unicodedata, bleach

SAFE_PUNCT = r""".,:;!?'"()[]{}@#$%^&*-_+=/\\|~"""
SAFE_CHARS = re.compile(fr"[^0-9A-Za-z\s{re.escape(SAFE_PUNCT)}]")
CONTROL_CHARS = ''.join(map(chr, list(range(0,32)) + [127]))
CONTROL_TABLE = str.maketrans('', '', CONTROL_CHARS)

def clean_text(s: str, max_len: int = 500) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.translate(CONTROL_TABLE)
    s = re.sub(r"[\u200B-\u200F\u202A-\u202E\u2066-\u2069]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = SAFE_CHARS.sub("", s)
    s = s[:max_len]
    s = bleach.clean(s, tags=[], attributes={}, strip=True)
    return s
