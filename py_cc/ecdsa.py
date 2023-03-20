from random import SystemRandom
from .elliptic_curves.baby_jubjub import BabyJubjubPoint, inverse, mulmod, addmod
from .keys import PrivateKey, PublicKey
from .hashes.sha256 import SHA
from .signature import Signature
from binascii import hexlify, unhexlify

class Ecdsa:

    @classmethod
    def sign(cls, message, private_key:PrivateKey, hash_fn=SHA):
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
    def verify(cls, message, signature:Signature, public_key: PublicKey, hash_fn=SHA):
        message_hash = hash_fn(message).digest()
        message_int = int.from_bytes(message_hash, byteorder='big')
        curve = public_key.curve
        generator = BabyJubjubPoint(curve.G[0], curve.G[1])

        if not 1 <= signature.r <= curve.n - 1 or not 1 <= signature.s <= curve.n - 1:
            return False
        

        inv = inverse(signature.s, curve.n)
        u1 = generator * message_int * inv
        u2 = public_key.point * signature.r * inv
        v = u1 + u2
        
        if v.isAtInfinity():
            return False
        
        print(v.x, signature.r)
        return v.x == signature.r
        