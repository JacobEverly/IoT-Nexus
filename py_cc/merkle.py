from .hashes.sha256 import SHA
from math import log2, ceil

def verify_merkle_proof(index, proof, commitment, hash_fn=SHA):
    if not proof:
        return hash_fn("").hexdigest() == commitment
    
    if len(proof) < 2:
        return proof[0] == commitment
    curr_hash = proof.pop(0)
    size = len(proof)
    while proof:
        bit_index = 1 << (size - 1)

        if index & bit_index == 0:
            curr_hash = hash_fn((curr_hash + proof.pop(0))).hexdigest()
        else:
            curr_hash = hash_fn((proof.pop(0) + curr_hash)).hexdigest()

        size -= 1
    return curr_hash == commitment
    # proof = proof.split(',')
    # if len(proof) < 2:
    #     return proof[0] == commitment
    
    # left = proof.pop(0).split(':')[1]
    # right = proof.pop(0).split(':')[1]
    # curr_hash = hash_fn((left + right)).hexdigest()
    # while proof:
    #     pos, hash = proof.pop(0).split(':')
    #     if pos == 'l':
    #         curr_hash = hash_fn((hash + curr_hash)).hexdigest()
    #     else:
    #         curr_hash = hash_fn((curr_hash + hash)).hexdigest()
    
    # return curr_hash == commitment

class MerkleTree:
    def __init__(self, leaves, hash_fn=SHA):
        self.leaves = leaves
        self._levels = 1 if len(leaves) <= 1 else 1 + ceil(log2(len(leaves)))
        self._treenodes = [None] * self._levels
        self._root = None
        self.hash_fn = hash_fn
        self.lsb_index = self.create_lsb_index()
        self._build()
    
    def create_lsb_index(self):
        def reverseBits(n):
            i = 0
            reverse = 0
            while i < self._levels - 1:
                x = (n >> i) & 1
                x <<= (self._levels - 2 - i)
                reverse = reverse | x
                i += 1
            return reverse
        lsb_index = map(reverseBits, range(len(self.leaves)))
        return list(lsb_index)
    
    def _build(self):
        if not self.leaves:
            self._treenodes[0] = [None]
            self._treenodes[0][0] = self.hash_fn("").hexdigest()
        elif len(self.leaves) == 1:
            self._treenodes[0] = [None]
            self._treenodes[0][0] = self.hash_fn(str(self.leaves[0])).hexdigest()
        else:
            # lsb_leaves = map(lambda x: self.leaves[x], self.lsb_index)
            for i in range(self._levels - 1):
                self._treenodes[i] = [None] * (1 << i)
            
            level = self._levels - 1
            self._treenodes[-1] = [self.hash_fn("").hexdigest()] * (1 << level)

            for i in range(len(self.leaves)):
                tree_index = self.lsb_index[i]
                self._treenodes[-1][tree_index] = self.hash_fn(str(self.leaves[i])).hexdigest()
            
            
            # for i in range(1 << level):
            #     if i < len(self.leaves):
            #         self._treenodes[level][i] = self.hash_fn(str(self.leaves[i])).hexdigest()
            #     else:
            #         self._treenodes[level][i] = self.hash_fn("").hexdigest()
            
            while level > 0:
                level -= 1
                for i in range(1 << level):
                    left = self._treenodes[level+1][2*i]
                    right = self._treenodes[level+1][2*i+1]
                    self._treenodes[level][i] = self.hash_fn((left + right)).hexdigest()
            
        self._root = self._treenodes[0][0]
    
    def get_root(self):
        return self._root
    
    def get_leaf(self, index):
        if index >= len(self.leaves):
            return None
        index = self.lsb_index[index]
        return self._treenodes[-1][index]

    def get_proof(self, index):
        if index >= len(self.leaves):
            return []
        elif len(self.leaves) == 1:
            return [self._root]
        else:
            _index = index
            tree_index = 0
            proof = []
            for level in range(1, self._levels):
                
                current_bit = _index & 1
                _index >>= 1
                on_left_side = current_bit == 0
                if level == self._levels - 1:
                    if on_left_side:
                        proof.insert(0, self._treenodes[level][tree_index + 1])
                        proof.insert(0, self._treenodes[level][tree_index])
                    else:
                        proof.insert(0, self._treenodes[level][tree_index])
                        proof.insert(0, self._treenodes[level][tree_index + 1])
                    break
                else:
                    if on_left_side:
                        proof.insert(0, self._treenodes[level][tree_index + 1])
                    else:
                        proof.insert(0, self._treenodes[level][tree_index])
                        tree_index += 1
                
                    tree_index *= 2
            return proof
            # for level in range(self._levels - 1, 0, -1):
            #     if level == self._levels - 1:
            #         if index % 2 == 0:
            #             proof.append(f"l:{self._treenodes[level][index]}")
            #             proof.append(f"r:{self._treenodes[level][index + 1]}")
            #         else:
            #             proof.append(f"l:{self._treenodes[level][index - 1]}")
            #             proof.append(f"r:{self._treenodes[level][index]}")
            #     else:
            #         if index % 2 == 0:
            #             proof.append(f"r:{self._treenodes[level][index + 1]}")
            #         else:
            #             proof.append(f"l:{self._treenodes[level][index - 1]}")
            #     index //= 2
            
            # return ','.join(proof)