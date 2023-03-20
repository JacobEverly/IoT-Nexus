from random import SystemRandom
from .elliptic_curves.baby_jubjub import BabyJubjubPoint, inverse, mulmod, addmod
from .keys import PrivateKey, PublicKey
from .hashes.sha256 import SHA
from .signature import Signature
from binascii import hexlify, unhexlify

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

class Eddsa:

    @classmethod
    def sign(cls, message, private_key:PrivateKey, public_key:PublicKey, hash_fn=SHA):
        pass
    
    @classmethod
    def verify(cls, message, signature:Signature, public_key: PublicKey, hash_fn=SHA):
        pass