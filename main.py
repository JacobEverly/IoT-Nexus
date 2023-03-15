# import random
from typing import Callable
from random import randint, randbytes
import random
import hashlib
from collections import defaultdict
import numpy as np

from py_cc.hashes import Poseidon, prime_254, matrix_254_3, round_constants_254_3
from py_cc.elliptic_curves.baby_jubjub import GeneratePoint


import argparse


class PoseidonHash(Poseidon):
    def __init__(
        self,
        prime=prime_254,
        security_level=128,
        input_rate=3,
        t=3,
        alpha=5,
        mds_matrix=matrix_254_3,
    ):
        """
        # TODO - add parameters description
        """
        super().__init__(
            prime, security_level, alpha, input_rate, t, mds_matrix=mds_matrix
        )

    def __str__(self) -> str:
        return "PoseidonHash"


class KeyPairGen:
    def __init__(self):
        self.ecc = GeneratePoint

    def getKeyPair(self):
        secret_key = randint(0, prime_254 - 1)
        public_key = secret_key * self.ecc
        return secret_key, public_key

    def getKeyPairs(self, num):
        """
        return a dictionary of key pairs in int format (not sure should be in hex or not)
        key: secret key
        value: public key (x, y)
        """
        print("Generate key pair")
        pairs = {}
        for i in range(num):
            while True:
                sk, pk = self.getKeyPair()
                if sk not in pairs:
                    pairs[sk] = pk
                    break
            print(f"Node: {i}")
            print(f"SK: {sk}")
            print(f"PK: {pk}")
            print("------------------")
        return pairs

    def __repr__(self):
        return f"Hash: {self.hash}, ECC: {self.ecc}"


def create_weights(PKs):
    weights = ()
    attesters = ()

    for i in range(0, len(PKs)):
        weight = np.random.randint(1, 1000)
        weights.append(weight)

    for i in range(len(PKs)):
        attesters = (PKs[i], weights[i])

    attesters = sorted(attesters, key=lambda x: x[1], reverse=True)
    provenWeight = sum(weights)

    return attesters, provenWeight


# Create Merkle tree of attestors (PK and weights)
def build_merkle_tree(elements):
    if len(elements) == 1:
        return elements[0][0].encode()

    # Combine adjacent pairs of elements and hash the result
    pairs = [
        (elements[i][0].encode() + elements[i + 1][0].encode())
        for i in range(0, len(elements), 2)
    ]
    if len(elements) % 2 == 1:
        pairs.append(elements[-1][0].encode() * 2)

    # Hash each pair of elements together and store the resulting hash value
    hashes = [hashlib.sha256(pair).digest() for pair in pairs]

    # Recursively build the Merkle tree from the list of hash values
    return build_merkle_tree(hashes)


# create range for each attestor by adding their weight to the previous attestor's range and marking the endpoints
def create_range(attesters, provenWeight):
    attestor_range = ()
    range_index = 0

    for i in range(len(attesters)):
        attestor_range = (attesters[i], range_index, range_index + attesters[i][1])
        range_index += attesters[i][1]

    return attestor_range


# Create merkle tree including Witness (Signed message by SK) and attestors range which is their spot in the provenweight


# Create Random Oracle that tells us the subrange that the prover should select a tree from
def random_oracle(merkle_root_hash):
    nonce = random.getrandbytes(8)
    # Hash the Merkle root hash and nonce value together
    h = hashlib.sha256(merkle_root_hash + nonce.to_bytes(8, "big")).digest()

    # Interpret the hash value as a number in the range from 0 to the sum of the weights
    random_number = int.from_bytes(h, "big") % 6
    return random_number


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Key Pairs")
    parser.add_argument(
        "-n", "--num", type=int, default=1, help="Number of key pairs to generate"
    )
    args = parser.parse_args()
    keyGen = KeyPairGen()
    pairs = keyGen.getKeyPairs(args.num)

    # attesters, provenWeight = create_weights(pairs)
    # # Extract the attesters and weights into separate lists
    # attesters = [attester[0] for attester in attesters]
    # weights = [attester[1] for attester in attesters]

    # # Combine each attester with its weight into a tuple
    # elements = list(zip(attesters, weights))

    # # Build the Merkle tree from the list of attesters and weights
    # root_hash = build_merkle_tree(elements)
    # # Print the root hash of the Merkle tree
    # print("Merkle root hash:", root_hash.hex())
