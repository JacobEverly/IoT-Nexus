from random import SystemRandom

from .elliptic_curves import BabyJubjubPoint
from .hashes import int_to_hex
from .hashes.sha256 import SHA

class PrivateKey:
    def __init__(self, curve, secret=None):
        self.curve = curve
        self.secret = secret or SystemRandom().randint(1, curve.n - 1)
    
    def get_public_key(self, hash_fn=SHA):
        generator = BabyJubjubPoint(self.curve.G[0], self.curve.G[1])
        publicPoint = self.secret * generator
        # scalar = int.from_bytes(hash_fn(self.secret).digest()[:self.curve.length], "big")
        # publicPoint = scalar * generator
        return PublicKey(self.curve, publicPoint)
    
    def toString(self):
        return int_to_hex(self.secret)[2:]
    
    def toBytes(self):
        return self.secret.to_bytes(self.curve.length, byteorder='big')
    
    def __repr__(self):
        return f"PrivateKey({self.toString()})"
    
    def __str__(self):
        return self.toString()
    
class PublicKey:
    def __init__(self, curve, point:BabyJubjubPoint):
        self.curve = curve
        self.point = point
    
    def toString(self, encode=False):
        y_hex = int_to_hex(self.point.y)[2:].zfill(self.curve.length)
        
        if encode:
            return "0004" + y_hex
        else:
            return y_hex
    
    def toBytes(self):
        return self.point.y.to_bytes(self.curve.length, byteorder='big')

    def __repr__(self):
        return f"PublicKey({self.toString()})"
    
    def __str__(self):
        return self.toString()