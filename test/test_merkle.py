import pytest
import random
import unittest
from py_cc.merkle import MerkleTree, verify_merkle_proof
from py_cc.hashes import SHA, toDigit
from py_cc.hashes import Poseidon, prime_254, matrix_254_3, round_constants_254_3

poseidon = Poseidon(
            prime_254,
            128,
            5,
            3,
            full_round=8,
            partial_round=57,
            mds_matrix=matrix_254_3,
            rc_list=round_constants_254_3,
        )

class TestMerkleTree(unittest.TestCase):
    def test_sha_empty(self):
        tree = MerkleTree([])
        self.assertEqual(tree.get_root(), SHA("").hexdigest())
    
    def test_sha_single(self):
        input = ['a']
        tree = MerkleTree(input)
        n = len(input)
        positive_indices = [random.randint(0, n-1) for x in range(4)]
        positive_indices += [0,n-1]
        negative_indices = [random.randint(n, 2*n) for x in range(2)]
        negative_indices += [n]
        for i in positive_indices:
            ret = tree.get_leaf(i)
            self.assertTrue(ret == input[i] or ret == SHA(input[i]).hexdigest())

        for i in negative_indices:
            ret = tree.get_proof(i)
            self.assertFalse(ret)
            ret = tree.get_leaf(i)
            self.assertFalse(ret)

    def test_sha_multiple(self):
        input = ['a', 'b', 'c', 'd', 'e']
        tree = MerkleTree(input)
        n = len(input)
        positive_indices = [random.randint(0, n-1) for x in range(4)]
        positive_indices += [0,n-1]
        negative_indices = [random.randint(n, 2*n) for x in range(2)]
        negative_indices += [n]
        for i in positive_indices:
            ret = tree.get_leaf(i)
            self.assertTrue(ret == input[i] or ret == SHA(input[i]).hexdigest())

        for i in negative_indices:
            ret = tree.get_proof(i)
            self.assertFalse(ret)
            ret = tree.get_leaf(i)
            self.assertFalse(ret)
    
    def test_verify_sha_empty(self):
        input = []
        tree = MerkleTree(input)
        proof = tree.get_proof(0)
        self.assertTrue(verify_merkle_proof(0, proof, tree.get_root()))
    
    def test_verify_sha_single(self):
        input = ['a']
        tree = MerkleTree(input)
        proof = tree.get_proof(0)
        self.assertTrue(verify_merkle_proof(0, proof, tree.get_root()))
    
    def test_verify_sha_multiple(self):
        input = ['a', 'b', 'c', 'd', 'e']
        tree = MerkleTree(input)
        n = len(input)
        indices = [random.randint(0, n-1) for x in range(4)]
        indices += [0,n-1]
        for idx in indices:
            pi = tree.get_proof(idx)
            self.assertTrue(verify_merkle_proof(idx, pi, tree.get_root()) or verify_merkle_proof(idx, pi, input[idx]))



    def test_poseidon_empty(self):
        tree = MerkleTree([], hash_fn=poseidon.run)
        self.assertEqual(tree.get_root(), poseidon.run("").hexdigest())
    
    def test_poseidon_single(self):
        input = ['a']
        tree = MerkleTree(input, hash_fn=poseidon.run)
        n = len(input)
        positive_indices = [random.randint(0, n-1) for x in range(4)]
        positive_indices += [0,n-1]
        negative_indices = [random.randint(n, 2*n) for x in range(2)]
        negative_indices += [n]
        for i in positive_indices:
            ret = tree.get_leaf(i)
            self.assertTrue(ret == input[i] or ret == poseidon.run(input[i]).hexdigest())

        for i in negative_indices:
            ret = tree.get_proof(i)
            self.assertFalse(ret)
            ret = tree.get_leaf(i)
            self.assertFalse(ret)

    def test_poseidon_multiple(self):
        input = ['a', 'b', 'c', 'd', 'e']
        tree = MerkleTree(input, hash_fn=poseidon.run)
        n = len(input)
        positive_indices = [random.randint(0, n-1) for x in range(4)]
        positive_indices += [0,n-1]
        negative_indices = [random.randint(n, 2*n) for x in range(2)]
        negative_indices += [n]
        for i in positive_indices:
            ret = tree.get_leaf(i)
            self.assertTrue(ret == input[i] or ret == poseidon.run(input[i]).hexdigest())

        for i in negative_indices:
            ret = tree.get_proof(i)
            self.assertFalse(ret)
            ret = tree.get_leaf(i)
            self.assertFalse(ret)
    
    def test_verify_poseidon_empty(self):
        input = []
        tree = MerkleTree(input, hash_fn=poseidon.run)
        proof = tree.get_proof(0)
        self.assertTrue(verify_merkle_proof(0, proof, tree.get_root(), hash_fn=poseidon.run))
    
    def test_verify_poseidon_single(self):
        input = ['a']
        tree = MerkleTree(input, hash_fn=poseidon.run)
        proof = tree.get_proof(0)
        self.assertTrue(verify_merkle_proof(0, proof, tree.get_root(), hash_fn=poseidon.run))
    
    def test_verify_poseidon_multiple(self):
        input = ['a', 'b', 'c', 'd', 'e']
        tree = MerkleTree(input, hash_fn=poseidon.run)
        n = len(input)
        indices = [random.randint(0, n-1) for x in range(4)]
        indices += [0,n-1]
        for idx in indices:
            pi = tree.get_proof(idx)
            self.assertTrue(verify_merkle_proof(idx, pi, tree.get_root(), hash_fn=poseidon.run) 
                            or verify_merkle_proof(idx, pi, input[idx], hash_fn=poseidon.run))


if __name__ == '__main__':
    unittest.main()