# import random
from hash import SHA
from typing import Callable
from random import randint, randbytes
from collections import defaultdict

from hash import PoseidonHash, prime_255, prime_254
from baby_jubjub import GeneratePoint

import argparse


class KeyPairGen:
    def __init__(self):
        self.hash = PoseidonHash()
        self.ecc = GeneratePoint

        self.t = 3 # TODO: try to remove this
    
    def getKeyPair(self):
        input_vec = [randint(0, prime_254 - 1) for _ in range(0, self.t)]
        poseidon_output = int(self.hash.run_hash(input_vec))
        print("Output: ", poseidon_output)

        secret_key = poseidon_output
        public_key = secret_key * self.ecc
        return secret_key, public_key
    
    def getKeyPairs(self, num):
        pairs = {}
        for _ in range(num):
            while True:
                sk, pk = self.getKeyPair()
                if sk not in pairs:
                    pairs[sk] = pk
                    break
        return pairs
                
    def __repr__(self):
        return f"Hash: {self.hash}, ECC: {self.ecc}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Key Pairs')
    parser.add_argument('-n', '--num', type=int, default=1, help='Number of key pairs to generate')
    args = parser.parse_args()
    keyGen = KeyPairGen()
    pairs = keyGen.getKeyPairs(args.num)
    print(pairs)
