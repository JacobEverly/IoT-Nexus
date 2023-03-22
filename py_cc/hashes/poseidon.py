import enum
import string
import numpy as np
import galois
from py_ecc.fields import FQ

from math import log2, ceil
from typing import Optional

from .utils import *

from .parameters import prime_64, prime_254, prime_255


class prime254_FQ(FQ):
    field_modulus = prime_254


class prime255_FQ(FQ):
    field_modulus = prime_255


class Hash:
    def __init__(self, value):
        self.value = value
    
    def hexdigest(self):
        """
        Return the digest value as a string of hexadecimal digits.
        """
        hash = int_to_hex(self.value)
        return hash[2:]

    def digest(self):
        """
        Return the digest value as a string of binary data.
        """
        return bytes.fromhex(self.hexdigest())

class Poseidon:
    def __init__(
        self,
        p,
        security_level,
        alpha,
        input_rate,
        t,
        full_round: Optional[int] = None,
        partial_round: Optional[int] = None,
        mds_matrix: Optional[list] = None,
        rc_list: Optional[list] = None,
        prime_bit_len: Optional[int] = None,
    ):
        """

        :param int p: The prime field modulus.
        :param int security_level: The security level measured in bits. Denoted `M` in the Poseidon paper.
        :param int alpha: The power of S-box.
        :param int input_rate: The size of input.
        :param int t: The size of Poseidon's inner state.
        :param int full_round: (optional) Number of full rounds. Denoted `R_F` in the Poseidon paper.
            If parameter is empty it will be calculated.
        :param int partial_round: (optional) Number of partial rounds. Denoted `R_P` in the Poseidon paper.
            If parameter is empty it will be calculated.
        :param list mds_matrix: (optional) 2-dim array of size t*t. Consist of field elements in hex representation.
            Can be calculated.
        :param list rc_list: (optional) List of size t*(full_round + partial_round).
            Consist of field elements in hex representation. Can be calculated.
        :param int prime_bit_len: (optional) The number of bits of the Poseidon prime field modulus. Denoted `n` in
            the Poseidon paper (where `n = ceil(log2(p))`). However for simplicity of calculation, the nearest degree
            of two can be used (for example 256 instead of 255). Using powers of two bits for simplicity when operating
            on bytes as the single bit difference does not affect the round number security properties.
        """
        # TODO: For now alpha is fixed parameter
        assert np.gcd(alpha, p - 1) == 1, "Not available alpha"
        assert 2**security_level <= p**t, "Not secure"

        # Initialize field
        if p == prime_254:
            self.FQ = prime254_FQ
        elif p == prime_255:
            self.FQ = prime255_FQ
        else:
            raise Exception("Not supported prime")
        # self.FQ = galois.GF(p)
        self.p = p
        self.t = t
        self.alpha = alpha
        self.security_level = security_level
        self.prime_bit_len = prime_bit_len if prime_bit_len else ceil(log2(p))
        # self.state = self.FQ.Zeros(self.t)
        self.state = [self.FQ(0) for _ in range(self.t)]
        self.rc_counter = 0  # round constant counter

        if full_round and partial_round:
            self.full_round = full_round
            self.partial_round = partial_round
            self.half_full_round = int(full_round / 2)
        else:
            rounds = calc_round_numbers(
                log2(self.p), self.security_level, self.t, self.alpha, True
            )
            self.full_round = rounds[0]
            self.partial_round = rounds[1]
            self.half_full_round = rounds[2]

        # Initialize round constants
        if rc_list:
            assert len(rc_list) == self.t * (
                self.full_round + self.partial_round
            ), "Invalid number of round constants"
            # self.round_constant = self.FQ([int(x, 16) for x in rc_list])
            self.round_constant = [self.FQ(int(x, 16)) for x in rc_list]
        else:
            self.round_constant = calc_round_constants(
                self.t,
                self.full_round,
                self.partial_round,
                self.p,
                self.FQ,
                self.alpha,
                self.prime_bit_len,
            )

        # Initialize MDS matrix
        if mds_matrix:
            assert (len(mds_matrix) == self.t) and (
                len(mds_matrix[0]) == self.t
            ), "Invalid size of MDS matrix"
            self.mds_matrix = get_field_matrix_from_hex_matrix(self.FQ, mds_matrix)
        else:
            self.mds_matrix = mds_matrix_generator(self.FQ, self.t)

    def s_box(self, element):
        return element**self.alpha

    def full_rounds(self):
        for _ in range(self.half_full_round):
            # add round constants, apply s-box
            for i in range(self.t):
                self.state[i] = self.state[i] + self.round_constant[self.rc_counter]
                self.rc_counter += 1

            for i in range(self.t):
                self.state[i] = self.s_box(self.state[i])
            # apply MDS matrix
            self.state = np.dot(self.mds_matrix, self.state)

    def partial_rounds(self):
        for _ in range(self.partial_round):
            # add round constants, apply s-box
            for i in range(self.t):
                self.state[i] = self.state[i] + self.round_constant[self.rc_counter]
                self.rc_counter += 1

            self.state[0] = self.s_box(self.state[0])

            # apply MDS matrix
            self.state = np.dot(self.mds_matrix, self.state)

    def run(self, message: string):
        """
        :param input_vec:
        :return:
        """
        if isinstance(message, str):
            m_encode = message.encode()
        elif isinstance(message, int):
            m_encode = message.to_bytes(32, byteorder="big")
        else:
            m_encode = message
        m_int = int.from_bytes(m_encode, byteorder="big")
        input_vec = [m_int]
        input_length = len(input_vec)
        if input_length < self.t:
            for i in range(input_length, self.t):
                input_vec.append(i)

        self.state = [self.FQ(val) for val in input_vec]
        # self.state = self.FQ(input_vec)
        self.rc_counter = 0

        self.full_rounds()
        self.partial_rounds()
        self.full_rounds()

        return Hash(self.state[0])

    # FOR TESTING
    def run_test(self, input_vec: list):
        """
        :param input_vec:
        :return:
        """
        if len(input_vec) < self.t:
            input_vec.extend([0] * (self.t - len(input_vec)))

        self.state = [self.FQ(val) for val in input_vec]
        # self.state = self.FQ(input_vec)
        self.rc_counter = 0

        self.full_rounds()
        self.partial_rounds()
        self.full_rounds()
        return self.state
