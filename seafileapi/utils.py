import string
import random
from urllib.parse import urlencode


def randstring(length=0):
    """Generiert einen Zufallsstring aus Kleinbuchstaben."""
    if length == 0:
        length = random.randint(1, 30)
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def urljoin(base, *args):
    """
    Baut eine URL zusammen.
    Achtung: Diese Funktion überschreibt die Standardfunktion `urljoin` 
    aus urllib.parse, ist also dein eigenes Custom-Join.
    """
    url = base
    if not url.endswith('/'):
        url += '/'
    for arg in args:
        arg = arg.strip('/')
        url += arg + '/'
    # Wenn in der finalen URL ein '?' vorkommt, wird der letzte Slash entfernt
    if '?' in url:
        url = url[:-1]
    return url


def to_utf8(obj):
    """
    Wandelt einen Python-String in Bytes im UTF-8-Format um.
    """
    if isinstance(obj, str):
        return obj.encode('utf-8')
    return obj


def querystr(**kwargs):
    """
    Erzeugt einen Query-String à la '?key1=val1&key2=val2'.
    """
    return '?' + urlencode(kwargs)


def utf8lize(obj):
    """
    Wandelt rekursiv alle Strings in Bytes (UTF-8) um, falls es sich um 
    Listen oder Dictionaries handelt.
    """
    if isinstance(obj, dict):
        return {k: to_utf8(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_utf8(x) for x in obj]
    if isinstance(obj, str):
        return obj.encode('utf-8')
    return obj
