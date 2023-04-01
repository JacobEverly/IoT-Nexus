import argparse

from py_cc.hashes import Poseidon, prime_254, matrix_254_3, round_constants_254_3
from py_cc.elliptic_curves.baby_jubjub import curve
from py_cc.certificate import CompactCertificate, Verification, Certificate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Key Pairs")
    parser.add_argument(
        "-n", "--num", type=int, default=2, help="Number of key pairs to generate"
    )
    args = parser.parse_args()

    message = "Hello World"
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
    CC = CompactCertificate(message, hash, curve, args.num)

    print("setAttestors")
    CC.setAttestors()

    print("signMessage")
    CC.signMessage()

    print("buildMerkleTree")
    CC.buildAttesterTree()
    CC.buildSignTree()

    print("createMap")
    CC.createMap()

    print("getCertificate")
    attester_tree, message, proven_weight, num_reveal, cert = CC.getCertificate()


    print("verifyCertificate")
    sigs_root = cert[0]
    signed_weight = cert[1]
    map_T = cert[2]
    V = Verification(sigs_root, signed_weight, map_T, attester_tree, message, proven_weight, hash)
    if not V.verifyCertificate():
        print("Certificate is invalid")
    else:
        print(f"Certificate is valid: {message}")

    print("Certificate JSON & DER & PEM")
    test = Certificate(message, "PoseidonHash", "BabyJubjub", "EdDSA", cert)
    test.toDER()
    test.toPEM()
    