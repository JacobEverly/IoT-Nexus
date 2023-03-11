from .hashes.sha256 import SHA
from math import log2, ceil

def verify_merkle_proof(proof, commitment):
    proof = proof.split(',')
    
    left = proof.pop(0).split(':')[1]
    right = proof.pop(0).split(':')[1]
    curr_hash = SHA(left + right)
    while proof:
        pos, hash = proof.pop(0).split(':')
        if pos == 'l':
            curr_hash = SHA(hash + curr_hash)
        else:
            curr_hash = SHA(curr_hash + hash)
    
    return curr_hash == commitment

class MerkleTree:
    def __init__(self, leaves):
        self.leaves = leaves
        self._levels = 1 + ceil(log2(len(leaves)))
        self._treenodes = [None] * self._levels
        self._root = None
        self._build()
    
    def _build(self):
        if not self.leaves:
            return SHA("")
        elif len(self.leaves) == 1:
            return SHA(str(self.leaves[0]))
        else:
            for i in range(self._levels):
                self._treenodes[i] = [None] * (1 << i)
            
            level = self._levels - 1
            for i in range(1 << level):
                if i < len(self.leaves):
                    self._treenodes[level][i] = SHA(str(self.leaves[i]))
                else:
                    self._treenodes[level][i] = SHA("")
            
            while level > 0:
                level -= 1
                for i in range(1 << level):
                    left = self._treenodes[level+1][2*i]
                    right = self._treenodes[level+1][2*i+1]
                    self._treenodes[level][i] = SHA(left + right)
            
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