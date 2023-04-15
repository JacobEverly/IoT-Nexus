import pytest
import unittest
from py_cc.keys import PrivateKey
from py_cc.eddsa import Eddsa
from py_cc.elliptic_curves.baby_jubjub import curve
from py_cc.hashes import Poseidon, prime_254, matrix_254_3, round_constants_254_3


class TestEddsa(unittest.TestCase):
    def test_basic(self):
        # eddsa
        hash = Poseidon(
            prime_254,
            128,
            5,
            3,
            full_round=8,
            partial_round=57,
            mds_matrix=matrix_254_3,
            rc_list=round_constants_254_3,
        )
        sk = PrivateKey(curve)
        pk = sk.get_public_key(hash.run)

        signature = Eddsa.sign("Hello World", sk, pk, hash.run)
        self.assertTrue(Eddsa.verify("Hello World", signature, pk, hash.run))

if __name__ == "__main__":
    unittest.main()