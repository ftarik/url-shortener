import random
import string
import re

def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_valid_url(url: str) -> bool:
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?.)+[A-Z]{2,6}.?|'
        r'localhost|'
        r'd{1,3}.d{1,3}.d{1,3}.d{1,3})'
        r'(?::d+)?'
        r'(?:/?|[/?]S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None
