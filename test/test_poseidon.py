import pytest
from py_cc.hashes import Poseidon, prime_254
import unittest

class TestPoseidon(unittest.TestCase):

    def test_hash(self):
        hash = Poseidon(prime_254, 128, 5, 3, 3)
        input_vec = [1, 2, 3]

if __name__ == '__main__':
    unittest.main()

