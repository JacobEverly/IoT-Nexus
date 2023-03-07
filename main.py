# import random
from hash import SHA
from typing import Callable
from random import randint, randbytes
import random

from hash import PoseidonHash, prime_255, prime_254
from baby_jubjub import GeneratePoint



class KeyPairGen:
    def __init__(self):
        self.hash = PoseidonHash()
        self.ecc = GeneratePoint

        self.t = 3 # TODO: try to remove this
    
    def getKeyPair(self):
        input_vec = [randint(0, prime_254 - 1) for _ in range(0, self.t)]
        poseidon_output = int(self.hash.run_hash(input_vec))
        print("Output: ", poseidon_output)

        public_key = poseidon_output
        secret_key = public_key * self.ecc
        return public_key, secret_key

    def __repr__(self):
        return f"Hash: {self.hash}, ECC: {self.ecc}"

if __name__ == "__main__":
    keyGen = KeyPairGen()
    pair = keyGen.getKeyPair()
    print(pair[0])
    print(pair[1])
