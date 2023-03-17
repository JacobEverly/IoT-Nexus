from hashlib import sha256
from random import SystemRandom
from .elliptic_curves.baby_jubjub import BabyJubjubPoint, inverse, mulmod, addmod
from .keys import PrivateKey, PublicKey

class Signature:
    def __init__(self, r, s, recovery_id=None):
        self.r = r
        self.s = s
        self.recovery_id = recovery_id

    def toString(self):
        return f"r:{self.r},s:{self.s}"

    def __str__(self):
        return f"r: {self.r}, s: {self.s}"
    
    def __repr__(self):
        return f"Signature({self.r}, {self.s}, {self.recovery_id})"

class Ecdsa:

    @classmethod
    def sign(cls, message, private_key, hash_fn=sha256):
        message_hash = hash_fn(message).digest()
        message_int = int.from_bytes(message_hash, byteorder='big')
        curve = private_key.curve
        generator = BabyJubjubPoint(curve.G[0], curve.G[1])

        r, s, randSignPoint = 0, 0, None
        while r == 0 or s == 0:
            rand = SystemRandom().randint(1, curve.n - 1)
            randSignPoint = generator * rand
            r = randSignPoint.x % curve.n
            s = (inverse(rand, curve.n) * (message_int + r * private_key.secret)) % curve.n
        
        recovery_id = randSignPoint.y & 1
        if recovery_id > curve.n:
            recovery_id += 2

        return Signature(r, s, recovery_id)
    
    @classmethod
    def verify(cls, message, signature:Signature, public_key: PublicKey, hash_fn=sha256):
        message_hash = hash_fn(message).digest()
        message_int = int.from_bytes(message_hash, byteorder='big')
        curve = public_key.curve
        generator = BabyJubjubPoint(curve.G[0], curve.G[1])

        if not 1 <= signature.r <= curve.n - 1 or not 1 <= signature.s <= curve.n - 1:
            return False
        

        inv = inverse(signature.s, curve.n)
        u1 = generator * (message_int * inv)
        u2 = public_key.point * (signature.r * inv)
        v = u1 + u2
        
        if v.isAtInfinity():
            return False

        return v == signature.r
        