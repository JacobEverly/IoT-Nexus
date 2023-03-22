from random import SystemRandom
from .elliptic_curves.baby_jubjub import BabyJubjubPoint, inverse, mulmod, addmod
from .keys import PrivateKey, PublicKey
from .hashes.sha256 import SHA
from .signature import Signature
from binascii import hexlify, unhexlify

# Reference: https://medium.com/asecuritysite-when-bob-met-alice/whats-the-difference-between-ecdsa-and-eddsa-e3a16ee0c966#:~:text=For%20improved%20security%2C%20ECDSA%20supports,compatibility%20with%20Bitcoin%20and%20Ethereum.

class Eddsa:

    @classmethod
    def sign(cls, message, private_key:PrivateKey, public_key:PublicKey, hash_fn=SHA):
        curve = private_key.curve
        generator = BabyJubjubPoint(curve.G[0], curve.G[1])
        en_msg = message.encode("utf-8")

        sk_hash = hash_fn(private_key.secret).digest()
        hash = hash_fn(sk_hash + en_msg).digest()

        r = int.from_bytes(hash, "big") % curve.n
        R = (r * generator)
        _R = R.y.to_bytes(curve.length, "big")

        h = int.from_bytes(hash_fn(_R + public_key.toBytes() + en_msg).digest(), "big") % curve.n

        # s = int.from_bytes(sk_hash, "big")
        S = (r + h * private_key.secret) % curve.n
        return Signature(R, S)
    
    @classmethod
    def verify(cls, message, signature:Signature, public_key: PublicKey, hash_fn=SHA):
        curve = public_key.curve
        generator = BabyJubjubPoint(curve.G[0], curve.G[1])
        en_msg = message.encode("utf-8")

        R = signature.r
        S = signature.s
        _R = R.y.to_bytes(curve.length, "big")
        k = int.from_bytes(hash_fn(_R + public_key.toBytes() + en_msg).digest(), "big") % curve.n

        P1 = S * generator
        P2 = R + k * public_key.point
        # print(P1, P2)
        return P1 == P2