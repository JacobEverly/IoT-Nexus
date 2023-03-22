# import random
from typing import Callable
from random import SystemRandom
import random
import hashlib
from math import log2, ceil

from py_cc.hashes import Poseidon, prime_254, matrix_254_3, round_constants_254_3
from py_cc.elliptic_curves.baby_jubjub import curve
from py_cc.keys import PrivateKey, PublicKey
from py_cc.eddsa import Eddsa
from py_cc.merkle import MerkleTree, verify_merkle_proof


import argparse

class Attestor:
    def __init__(self, private_key:PrivateKey=None, public_key:PublicKey=None, weight=None):
        self.__private_key = private_key
        self.public_key = public_key
        self.weight = weight

    def getPrivateKey(self):
        return self.__private_key
    
    def setPublicKey(self, public_key):
        self.public_key = public_key

    def setWeight(self, weight):
        self.weight = weight

    def __repr__(self):
        return f"PK: {self.public_key}, SK: {self.__private_key}, Weight: {self.weight}"
    
    def __eq__(self, other) -> bool:
        return self.public_key == other.public_key and self.weight == other.weight

class CompactCertificate:
    def __init__(self, message, hash, curve, attesters=0):
        self.message = message
        self.hash = hash
        self.curve = curve
        self.attesters = [None] * attesters
        self.attester_tree = None
        self.signatures = [None] * len(self.attesters)
        self.signers = {} # key: index in attesters, value: signature
        self.sigs_tree = None
        self.signed_weight = 0
        self.proven_weight = 0
        self.total_weight = 0
        self.map_T = {}

    def setAttestors(self):
        total_weight = 0
        for i in range(len(self.attesters)):
            sk = PrivateKey(self.curve)
            pk = sk.get_public_key()
            weight = SystemRandom().randrange(1, 1000)
            total_weight += weight
            
            self.attesters[i] = Attestor(sk, pk, weight)
        self.attesters = sorted(self.attesters, key=lambda x: x.weight, reverse=True)
        self.total_weight = total_weight
        self.proven_weight = 0.51 * total_weight

    def signMessage(self):
        """
        create signatures list with the following format: (signature, left_value, right_value)
        length of signatures list is the same as the length of attesters list
        atterters in signatures list that are not signers will have empty signature with L = R
        """
        while self.signed_weight < self.proven_weight or len(self.signers) < 2:
            i = SystemRandom().randrange(0, len(self.attesters))
            if i in self.signers:
                continue
            sk = self.attesters[i].getPrivateKey()
            signature = Eddsa.sign(self.message, sk, self.attesters[i].public_key, hash_fn=self.hash.run)
            
            if not Eddsa.verify(self.message, signature, self.attesters[i].public_key, hash_fn=self.hash.run):
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
                self.signatures[i] = (sig, L, R)
            else:
                R = L
                self.signatures[i] = ("", L, R)
            L = R

    def verifySignatures(self):
        for i in range(len(self.attesters)):
            pk = self.attesters[i].public_key
            signature = self.signatures[i]
            if not Eddsa.verify(self.message, signature, pk, hash_fn=self.hash.run):
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
        for signature in self.signatures:
            signatures.append(str(signature)) # signature, left_value, right_value

        self.sigs_tree = MerkleTree(signatures, hash_fn=self.hash.run)

    def createMap(self):
        """
        Create a map(T) of the attestors that signed the message for verification
        """
        k = 64 # we dont't know what k and q is yet
        q = 64
        self.num_reveals = ceil((k + q)/ log2(self.signed_weight/self.proven_weight))
        sigs_root = self.sigs_tree.get_root()
        attester_root = self.attester_tree.get_root()
        for j in range(self.num_reveals):
            hin = (j, sigs_root, self.proven_weight, self.message, attester_root)
            coin = int.from_bytes(self.hash.run(str(hin)).digest(), "big") % (self.signed_weight - 1) + 1
            idx = self.intToIdx(coin)

            assert idx != -1, "Coin is not in range"
            if idx not in self.map_T:
                self.map_T[idx] = (
                    (self.signatures[idx][0], self.signatures[idx][1]), # with R value
                    self.sigs_tree.get_proof(idx), # merkle proof of signature
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
            

            if coin > R:
                low = mid + 1
            elif coin <= L:
                high = mid - 1

        return -1
    
    def getCertificate(self):
        sigs_root = self.sigs_tree.get_root()
        attester_root = self.attester_tree.get_root()
        return (
            # self.attester_tree,
            attester_root,
            self.message, 
            self.proven_weight, 
            self.num_reveals,
            (sigs_root, self.signed_weight, self.map_T), # The map T in the paper
        )
        

class Verification:
    # attester_tree, message, proven_weight, sign_weight, map T
    def __init__(self, sigs_root, signed_weight, map_T, num_reveal, attester_root, message, proven_weight, hash):
        self.sigs_root = sigs_root
        self.signed_weight = signed_weight
        self.map_T = map_T
        self.num_reveal = num_reveal
        self.message = message
        self.proven_weight = proven_weight
        self.attester_root = attester_root
        self.hash = hash

        # self.signature = reveal[0][0]
        # self.L = reveal[0][1]
        # self.sigs_proof = reveal[1]
        # self.attester = reveal[2]
        # self.attester_proof = reveal[3]

    def verifyCertificate(self):
        # Make sure signed weight is greater than proven weight on cerificate
        if self.signed_weight < self.proven_weight:
            return False
        
        #Checks to make sure data is valid on certificate
        for idx, reveal in self.map_T.items():
            signature = reveal[0][0]
            L = reveal[0][1]
            sigs_proof = reveal[1]
            attester = reveal[2]
            attester_proof = reveal[3]

            # Make sure that paths are valid for given index in respect to Sig Tree
            if not verify_merkle_proof(sigs_proof, self.sigs_root, self.hash.run):
                print("sign_proof invalid")
                return False
            
            #check vector commitments are valid for mapping
            if not verify_merkle_proof(attester_proof, self.attester_root, self.hash.run):
                print("attester_proof invalid")
                return False
            
            # Make sure signature on M is a valid key in ground truth
            public_key = attester.public_key
            if not Eddsa.verify(self.message, signature, public_key, hash_fn=self.hash.run):
                print("signature invalid")
                return False
            
            if not self.verifyCoin(signature, L, sigs_proof, attester, attester_proof):
                print("no coin get match this signature")
                return False
        
        return True
    
    def verifyCoin(self, signature, L, sigs_proof, attester, attester_proof):
        for j in range(self.num_reveal):
            hin = (j, self.sigs_root, self.proven_weight, self.message, self.attester_root)
            coin = int.from_bytes(self.hash.run(str(hin)).digest(), "big") % (self.signed_weight - 1) + 1
            
            for pos, t in self.map_T.items():
                
                t_sig = t[0][0]
                t_L = t[0][1]
                t_sigs_proof = t[1]
                t_attester = t[2]
                t_attester_proof = t[3]
                if t_L < coin <= (t_L + t_attester.weight):
                    if t_sig == signature and t_L == L and t_sigs_proof == sigs_proof and t_attester == attester and t_attester_proof == attester_proof:
                        return True
                    else:
                        continue
        
        return False


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
        "-n", "--num", type=int, default=2, help="Number of key pairs to generate"
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
    attester_tree, message, proven_weight, num_reveal, cert = CC.getCertificate()


    print("verifyCertificate")
    valid = True
    sigs_root = cert[0]
    signed_weight = cert[1]
    map_T = cert[2]
    V = Verification(sigs_root, signed_weight, map_T, num_reveal, attester_tree, message, proven_weight, hash)
    if not V.verifyCertificate():
        print("Certificate is invalid")
    else:
        print(f"Certificate is valid: {message}")

    # for j, reveal in enumerate(map_T.items()):
        
    #     p, passed = 
    #     if not passed or p != j:
    #         valid = False
    #         break
    
    # if valid:
    #     print(f"Certificate is valid: {message}")
    # else:
    #     print("Certificate is invalid")

    