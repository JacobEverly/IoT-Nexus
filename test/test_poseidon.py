import pytest
from py_cc.hashes import (
    Poseidon,
    prime_254,
    matrix_254_3,
    matrix_254_5,
    round_constants_254_3,
    round_constants_254_5,
)
from py_cc.hashes import (
    prime_255,
    matrix_255_3,
    matrix_255_5,
    round_constants_255_3,
    round_constants_255_5,
)
from py_cc.hashes import int_to_hex
import unittest


class TestPoseidon(unittest.TestCase):
    def test_hash_255_3(self):
        # poseidonperm_x5_255_3
        hash = Poseidon(
            prime_255,
            128,
            5,
            3,
            3,
            full_round=8,
            partial_round=57,
            mds_matrix=matrix_255_3,
            rc_list=round_constants_255_3,
        )

        input = [0, 1, 2]
        gts = [
            "0x28ce19420fc246a05553ad1e8c98f5c9d67166be2c18e9e4cb4b4e317dd2a78a",
            "0x51f3e312c95343a896cfd8945ea82ba956c1118ce9b9859b6ea56637b4b1ddc4",
            "0x3b2b69139b235626a0bfb56c9527ae66a7bf486ad8c11c14d1da0c69bbe0f79a",
        ]

        outputs = hash.run_test(input)
        for output, gt in zip(outputs, gts):
            self.assertEqual(int_to_hex(output, 255), gt)

    def test_hash_255_5(self):
        # poseidonperm_x5_255_5
        hash = Poseidon(
            prime_255,
            128,
            5,
            5,
            5,
            full_round=8,
            partial_round=60,
            mds_matrix=matrix_255_5,
            rc_list=round_constants_255_5,
        )

        input = [0, 1, 2, 3, 4]
        gts = [
            "0x2a918b9c9f9bd7bb509331c81e297b5707f6fc7393dcee1b13901a0b22202e18",
            "0x65ebf8671739eeb11fb217f2d5c5bf4a0c3f210e3f3cd3b08b5db75675d797f7",
            "0x2cc176fc26bc70737a696a9dfd1b636ce360ee76926d182390cdb7459cf585ce",
            "0x4dc4e29d283afd2a491fe6aef122b9a968e74eff05341f3cc23fda1781dcb566",
            "0x03ff622da276830b9451b88b85e6184fd6ae15c8ab3ee25a5667be8592cce3b1",
        ]
        outputs = hash.run_test(input)
        for output, gt in zip(outputs, gts):
            self.assertEqual(int_to_hex(output), gt)

    def test_hash_254_3(self):
        # poseidonperm_x5_254_3
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

        input = [0, 1, 2]
        gts = [
            "0x115cc0f5e7d690413df64c6b9662e9cf2a3617f2743245519e19607a4417189a",
            "0x0fca49b798923ab0239de1c9e7a4a9a2210312b6a2f616d18b5a87f9b628ae29",
            "0x0e7ae82e40091e63cbd4f16a6d16310b3729d4b6e138fcf54110e2867045a30c",
        ]
        outputs = hash.run_test(input)
        for output, gt in zip(outputs, gts):
            self.assertEqual(int_to_hex(output), gt)

        message = "Hello World"
        output = hash.run(message)
        gt = "0x2b3786c684606afd5bbb4e288e6bd85c44402eac88b895e4bfce0ea58d03aa81"
        self.assertEqual(int_to_hex(output.value), gt)

    def test_hash_254_5(self):
        # poseidonperm_x5_254_5
        hash = Poseidon(
            prime_254,
            128,
            5,
            5,
            5,
            full_round=8,
            partial_round=60,
            mds_matrix=matrix_254_5,
            rc_list=round_constants_254_5,
        )
        input = [0, 1, 2, 3, 4]
        gts = [
            "0x299c867db6c1fdd79dcefa40e4510b9837e60ebb1ce0663dbaa525df65250465",
            "0x1148aaef609aa338b27dafd89bb98862d8bb2b429aceac47d86206154ffe053d",
            "0x24febb87fed7462e23f6665ff9a0111f4044c38ee1672c1ac6b0637d34f24907",
            "0x0eb08f6d809668a981c186beaf6110060707059576406b248e5d9cf6e78b3d3e",
            "0x07748bc6877c9b82c8b98666ee9d0626ec7f5be4205f79ee8528ef1c4a376fc7",
        ]
        outputs = hash.run_test(input)
        for output, gt in zip(outputs, gts):
            self.assertEqual(int_to_hex(output), gt)

    # def test_hash_256(self):
    #     hash = Poseidon(prime_256, 128, 5, 3, 3)
    #     # starkadperm_x5_256_3
    #     input = ['0x0000000000000000000000000000000000000000000000000000000000000000', '0x0000000000000000000000000000000000000000000000000000000000000001', '0x0000000000000000000000000000000000000000000000000000000000000002']
    #     gt = ['0xd4a965f154ff8634896b30da71a3b5dfdbf8f87bba6dd053c7dc32b289464a50', '0x21edf7423857b5fd375ac0808409b50e7b92c580fe0b8415bb0a8cf352995118', '0x73b5e0fb2390fd139c9fa8a3e3a2c2349e504b02f80eef19e434070fa4ce147d']


if __name__ == "__main__":
    unittest.main()
