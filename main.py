# import random
from typing import Callable
from random import SystemRandom
import random
import hashlib
from math import log2, ceil

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
    def __init__(self, message, hash, curve, attesters=0):
        self.message = message
        self.hash = hash
        self.curve = curve
        self.attesters = [Attestor()] * attesters
        self.attester_tree = None
        self.signatures = [None] * len(self.attesters)
        self.signers = {} # key: index in attesters, value: signature
        self.sign_tree = None
        self.signed_weight = 0
        self.proven_weight = 0
        self.total_weight = 0
        self.reveals = {}

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
        self.proven_weight = 0.51 * total_weight

    def signMessage(self):
        """
        create signatures list with the following format: (signature, left_value, right_value)
        length of signatures list is the same as the length of attesters list
        atterters in signatures list that are not signers will have empty signature with L = R
        """
        while self.signed_weight < self.proven_weight:
            i = SystemRandom().randrange(0, len(self.attesters))
            if i in self.signers:
                continue
            sk = self.attesters[i].private_key
            signature = Ecdsa.sign(self.message, sk, hash_fn=self.hash.run)

            if not Ecdsa.verify(self.message, signature, self.attesters[i].public_key, hash_fn=self.hash.run):
                print("Signature is not valid")
                continue
            
            self.signers[i] = signature
            self.signed_weight += self.attesters[i].weight
        
        assert len(self.signers) > 1, "Not enough signatures, must be signed by at least 2 attestors"
        # self.signatures = sorted(self.signatures, key=lambda x: x[1], reverse=True)

        # create sigs list with same length as attesters list
        L = 0
        for i in range(len(self.signatures)):
            if i in self.signers:
                # signature, left_value, right_value to self.signatures
                R = L + self.attesters[i].weight
                sig = self.signers[i]
                self.signatures[i] = (sig.toString(), L, R)
            else:
                R = L
                self.signatures[i] = ("", L, R)
            L = R

    def verifySignatures(self):
        for i in range(len(self.attesters)):
            pk = self.attesters[i].public_key
            signature = self.signatures[i]
            if not Ecdsa.verify(self.message, signature, pk, hash_fn=self.hash.run):
                return False
        return True
    
    def buildAttesterTree(self):
        """
        Create merkle tree including attestors public keys
        """
        pks = [attester.public_key.toString() for attester in self.attesters]
        self.attester_tree = MerkleTree(pks, hash_fn=self.hash.run)

    def buildSignTree(self):
        """
        Create merkle tree including Witness (Signed message by SK) and attestors range which is their spot in the provenweight
        """
        signatures = []
        for signature, L, R in self.signatures:
            signatures.append(signature + "," + str(L) + "," + str(R)) # signature, left_value, right_value

        self.sign_tree = MerkleTree(signatures, hash_fn=self.hash.run)

    def createMap(self):
        """
        Create a map(T) of the attestors that signed the message for verification
        """
        k = 1
        q = 1
        number_reveals = ceil((k + q)/ log2(self.signed_weight/self.proven_weight))
        for j in range(number_reveals):
            hin = (j, self.sign_tree.get_root(), self.proven_weight, self.message, self.attester_tree.get_root())
            coin = int(self.hash.run(str(hin)).value) % self.signed_weight
            idx = self.intToIdx(coin)
            assert idx != -1, "Coin is not in range"
            if idx not in self.reveals:
                self.reveals[idx] = (
                    (self.signatures[idx][0], self.signatures[idx][1]), # with R value
                    self.sign_tree.get_proof(idx), # merkle proof of signature
                    self.attesters[idx],
                    self.attester_tree.get_proof(idx) # merkle proof of attester?? not sure is all attestors or just the one that signed, refer p5 step 6
                )
    
    def intToIdx(self, coin):
        """
        Returns the index of the signature that contains the coin, binary search
        """
        low = 0
        high = len(self.signatures) - 1
        while low <= high:
            mid = (low + high) // 2
            L = self.signatures[mid][1]
            R = self.signatures[mid][2]
            if L < coin <= R and L != R:
                return mid
            

            if coin >= R:
                low = mid + 1
            elif coin <= self.signatures[mid][1]:
                high = mid - 1

        return -1
    
    def getCertificate(self):
        return (
            self.sign_tree.get_root(),
            self.reveals, # The map T in the paper
        )


def verify_merkle_tree(tree:MerkleTree, commitment, proof, hash_fn:Callable[[str], int]):
    index = random_oracle(tree.get_root())
    proof = tree.get_proof(index)

    return verify_merkle_proof(proof, commitment, hash_fn=hash_fn)


# Create Random Oracle that tells us the subrange that the prover should select a tree from
def random_oracle(merkle_root_hash, modulus):
    nonce = random.getrandbytes(8)
    # Hash the Merkle root hash and nonce value together
    h = hashlib.sha256(merkle_root_hash + nonce.to_bytes(8, "big")).digest()

    # Interpret the hash value as a number in the range from 0 to the sum of the weights
    random_number = int.from_bytes(h, "big") % modulus
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
    CC = CompactCertificate("Hello World", hash, curve, args.num)

    print("setAttestors")
    CC.setAttestors()

    print("signMessage")
    CC.signMessage()

    print("buildMerkleTree")
    CC.buildAttesterTree()
    CC.buildSignTree()

    print("createMap")
    CC.createMap()

    print("getCertificate")
    cert = CC.getCertificate()
    print(cert)
