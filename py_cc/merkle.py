from hashlib import sha256
from math import log2, ceil

def verify_merkle_proof(proof, commitment, hash_fn=sha256):
    proof = proof.split(',')
    
    left = proof.pop(0).split(':')[1]
    right = proof.pop(0).split(':')[1]
    curr_hash = hash_fn(left + right).hexdigest()
    while proof:
        pos, hash = proof.pop(0).split(':')
        if pos == 'l':
            curr_hash = hash_fn(hash + curr_hash).hexdigest()
        else:
            curr_hash = hash_fn(curr_hash + hash).hexdigest()
    
    return curr_hash == commitment

class MerkleTree:
    def __init__(self, leaves, hash_fn=sha256):
        self.leaves = leaves
        self._levels = 1 + ceil(log2(len(leaves)))
        self._treenodes = [None] * self._levels
        self._root = None
        self.hash_fn = hash_fn
        self._build()
    
    def _build(self):
        if not self.leaves:
            return self.hash_fn("").hexdigest()
        elif len(self.leaves) == 1:
            return self.hash_fn(str(self.leaves[0])).hexdigest()
        else:
            for i in range(self._levels):
                self._treenodes[i] = [None] * (1 << i)
            
            level = self._levels - 1
            for i in range(1 << level):
                if i < len(self.leaves):
                    self._treenodes[level][i] = self.hash_fn(str(self.leaves[i])).hexdigest()
                else:
                    self._treenodes[level][i] = self.hash_fn("").hexdigest()
            
            while level > 0:
                level -= 1
                for i in range(1 << level):
                    left = self._treenodes[level+1][2*i]
                    right = self._treenodes[level+1][2*i+1]
                    self._treenodes[level][i] = self.hash_fn(left + right).hexdigest()
            
            self._root = self._treenodes[0][0]
    
    def get_root(self):
        return self._root
    
    def get_proof(self, index):
        assert index < len(self.leaves), "Index out of the range of leaves"

        proof = []
        for level in range(self._levels - 1, 0, -1):
            if level == self._levels - 1:
                if index % 2 == 0:
                    proof.append(f"l:{self._treenodes[level][index]}")
                    proof.append(f"r:{self._treenodes[level][index + 1]}")
                else:
                    proof.append(f"l:{self._treenodes[level][index - 1]}")
                    proof.append(f"r:{self._treenodes[level][index]}")
            else:
                if index % 2 == 0:
                    proof.append(f"r:{self._treenodes[level][index + 1]}")
                else:
                    proof.append(f"l:{self._treenodes[level][index - 1]}")
            index //= 2
        
        return ','.join(proof)