import random
from hash import SHA
from typing import Callable
import string

def KeyPairGen(d: int, r: int, hash_fc: Callable[[str], str]) -> dict:
    pairs = {}
    random.seed(r)
    for _ in range(1 << d):
        cur = random.randbytes(32).hex()
        while cur in pairs:
            cur = random.randbytes(32).hex()
        pairs[cur] = hash_fc(cur)
    return pairs

if __name__ == "__main__":
    d = 3
    r = 123
    pairs = KeyPairGen(d, r, SHA)
    print(pairs)
