from .hashes import int_to_hex
from py_ecc.fields import FQ


class Signature:
    def __init__(self, r, s, recovery_id=None):
        self.r = r
        self.s = s
        self.recovery_id = recovery_id

    def toString(self):
        return (int_to_hex(self.r.y)[2:], int_to_hex(self.s)[2:])

    def __eq__(self, other):
        return (self.r == other.r) and (self.s == other.s)

    def __str__(self):
        return f"r:{self.r},s:{self.s}"

    def __repr__(self):
        return f"Signature({self.r},{self.s},{self.recovery_id})"
