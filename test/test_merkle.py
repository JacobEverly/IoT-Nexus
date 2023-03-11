import pytest
import unittest
from py_cc.merkle import MerkleTree, verify_merkle_proof
from py_cc.hashes import SHA

class TestMerkleTree(unittest.TestCase):
    def test_empty(self):
        tree = MerkleTree([])
        assert tree.get_root() == SHA("")

if __name__ == '__main__':
    unittest.main()