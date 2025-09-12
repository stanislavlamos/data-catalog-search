import re, unicodedata
from bs4 import BeautifulSoup


def strip_text(txt: str) -> str:
    return txt.strip()

def to_lower(txt: str) -> str:
    return txt.lower()

def remove_html(txt: str) -> str:
    return BeautifulSoup(txt, "html.parser").get_text()

def normalize_unicode(txt: str) -> str:
    return unicodedata.normalize("NFC", txt)

def replace_newlines_and_tabs(txt: str) -> str:
    return re.sub(r"\s+", " ", txt)

def clean_text(txt: str) -> str:
    stripped = strip_text(txt)
    lower = to_lower(stripped)
    html_removed = remove_html(lower)
    unicode_removed = normalize_unicode(html_removed)
    cleaned_txt = replace_newlines_and_tabs(unicode_removed)

    return cleaned_txt
