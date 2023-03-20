import string
import hashlib
def SHA(s: string):
    return hashlib.sha256(s.encode())
