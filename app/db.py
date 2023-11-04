from py_cc.certificate import Attestor
from py_cc.elliptic_curves.baby_jubjub import curve
from py_cc.keys import PrivateKey

N_ATTESTORS = 10
N_MESSAGES = 10
attenstors = {}

for _ in range(N_ATTESTORS):
    private_key = PrivateKey(curve)
    public_key = private_key.get_public_key()
    att = Attestor(private_key, public_key)
    attenstors[att.public_key.toString()] = att

messages = {}


def get_attestor(attestor_s):
    return attenstors[attestor_s]


def save_signed_message(message: str, signature):
    messages[message] = signature
