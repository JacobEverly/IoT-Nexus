# import random
from typing import Callable
from random import SystemRandom
import random
import hashlib

from py_cc.hashes import Poseidon, prime_254, matrix_254_3, round_constants_254_3
from py_cc.elliptic_curves.baby_jubjub import curve
from py_cc.keys import PrivateKey, PublicKey
from py_cc.ecdsa import Ecdsa
from py_cc.merkle import MerkleTree, verify_merkle_proof


import argparse

class Attestor:
    def __init__(self, private_key:PrivateKey=None, public_key:PublicKey=None, weight=None):
        self.private_key = private_key
        self.public_key = public_key
        self.weight = weight

    def setPrivateKey(self, private_key):
        self.private_key = private_key
    
    def setPublicKey(self, public_key):
        self.public_key = public_key

    def setWeight(self, weight):
        self.weight = weight

    def __repr__(self):
        return f"PK: {self.public_key}, SK: {self.private_key}, Weight: {self.weight}"

class CompactCertificate:
    def __init__(self, hash, curve, attesters=0):
        self.hash = hash
        self.curve = curve
        self.attesters = [Attestor()] * attesters
        self.attester_tree = None
        self.signatures = []
        self.sign_tree = None
        self.total_weight = 0

    def setAttestors(self):
        total_weight = 0
        for i in range(len(self.attesters)):
            sk = PrivateKey(self.curve)
            pk = sk.get_public_key()
            weight = SystemRandom().randrange(1, 1000)
            total_weight += weight

            self.attesters[i].setPrivateKey(sk)
            self.attesters[i].setPublicKey(pk)
            self.attesters[i].setWeight(weight)
            
        self.attesters = sorted(self.attesters, key=lambda x: x.weight, reverse=True)
        self.total_weight = total_weight

    def signMessage(self, message):
        for i in range(len(self.attesters)):
            sk = self.attesters[i].private_key
            signature = Ecdsa.sign(message, sk, hash_fn=self.hash.run)
            self.signatures.append(signature)

    def verifySignatures(self, message):
        for i in range(len(self.attesters)):
            pk = self.attesters[i].public_key
            signature = self.signatures[i]
            if not Ecdsa.verify(message, signature, pk, hash_fn=self.hash.run):
                return False
        return True
    
    def buildAttesterTree(self):
        pks = [attester.public_key.toString() for attester in self.attesters]
        self.attester_tree = MerkleTree(pks, hash_fn=self.hash.run)

    # Create merkle tree including Witness (Signed message by SK) and attestors range which is their spot in the provenweight
    def buildSignTree(self):
        weights = [attester.weight for attester in self.attesters]
        signatures = [signature.toString()+","+weight for signature, weight in zip(self.signatures, weights)]
        self.sign_tree = MerkleTree(signatures, hash_fn=self.hash.run)
    



def verifyMerkleTree(tree:MerkleTree, commitment, proof, hash_fn:Callable[[str], int]):
    index = random_oracle(tree.get_root())
    proof = tree.get_proof(index)

    return verify_merkle_proof(proof, commitment, hash_fn=hash_fn)



# create range for each attestor by adding their weight to the previous attestor's range and marking the endpoints
def create_weight_range(attesters):
    attesters_range = []
    left_value = 0

    for attester in attesters:
        attesters_range.append(f"w:(${attester.weight},${left_value},${left_value + attester.weight})")
        left_value += attester.weight

    return attesters_range



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

    hash = Poseidon(
            prime_254,
            128,
            5,
            3,
            3,
            full_round=8,
            partial_round=57,
            mds_matrix=matrix_254_3,
            rc_list=round_constants_254_3,
        )
    CC = CompactCertificate(hash, curve, args.num)
    CC.setAttestors()
    print("Attestors: ", CC.attesters)
    
