from random import SystemRandom

from .elliptic_curves import BabyJubjubPoint
from .hashes import int_to_hex

class PrivateKey:
    def __init__(self, curve, secret=None):
        self.curve = curve
        self.secret = secret or SystemRandom().randint(1, curve.n - 1)
    
    def get_public_key(self):
        generator = BabyJubjubPoint(self.curve.G[0], self.curve.G[1])
        publicPoint = generator * self.secret
        return PublicKey(self.curve, publicPoint)
    
    def toString(self):
        return int_to_hex(self.secret)[2:]
    
    def __repr__(self):
        return f"PrivateKey({self.toString()})"
    
    def __str__(self):
        return self.toString()
    
class PublicKey:
    def __init__(self, curve, point:BabyJubjubPoint):
        self.curve = curve
        self.point = point
    
    def toString(self, encode=False):
        x_hex = int_to_hex(self.point.x)[2:].zfill(self.curve.length)
        y_hex = int_to_hex(self.point.y)[2:].zfill(self.curve.length)
        
        if encode:
            return "0004" + x_hex + y_hex
        else:
            return x_hex + y_hex
        
    def __repr__(self):
        return f"PublicKey({self.toString()})"
    
    def __str__(self):
        return self.toString()