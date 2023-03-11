import string
import hashlib

def SHA(s: string) -> string:
    return hashlib.sha256(s.encode()).hexdigest()
