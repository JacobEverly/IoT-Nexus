import argparse
import json
import time

from py_cc.hashes import toDigit
from py_cc.hashes import Poseidon, prime_254, matrix_254_3, round_constants_254_3
from py_cc.elliptic_curves.baby_jubjub import curve
from py_cc.certificate import CompactCertificate, Verification, Certificate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Key Pairs")
    parser.add_argument(
        "-n", "--num", type=int, default=2, help="Number of key pairs to generate"
    )
    parser.add_argument(
        "-m",
        "--message",
        type=str,
        default="Hello World!",
        help="Number of key pairs to generate",
    )
    args = parser.parse_args()

    start = time.time()
    message = args.message
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
    # res = hash.run(100).plain()
    # print(res)
    # exit(0)
    CC = CompactCertificate(message, hash, curve, args.num)

    # print("CollectAttestors")
    # CC.setAttestors()
    CC.setAttestorsFromFile()  # TODO: remove this

    # print("signMessage")
    CC.signMessage()  # TODO: remove this

    # when the expiration data arrived, then execute the following code
    print("buildMerkleTree")
    CC.buildAttesterTree()
    CC.buildSignTree()

    print("createMap")
    CC.createMap()

    print("getCertificate")
    attester_root, message, proven_weight, cert, coins = CC.getCertificate()

    # we save the certificate into a json file then pass to Zokrates to generate proof
    print("Certificate JSON")
    test = Certificate(message, "PoseidonHash", "BabyJubjub", "EdDSA", cert)
    cert_json = test.toJSON()
    with open("zokratesjs/verify.json", "w") as file:
        verify_json = [
            {
                "message": f"0x{hash.run(message).hexdigest()}",
            },
            {
                "attester_root": f"0x{attester_root}",
                "proven_weight": f"{proven_weight}",
            },
            cert_json["certificate"],
            coins,
        ]
        json.dump(verify_json, file, indent=4)
    file.close()
    with open("zokrates/verify.json", "w") as file:
        verify_json = [
            {
                "message": f"0x{hash.run(message).hexdigest()}",
            },
            {
                "attester_root": f"0x{attester_root}",
                "proven_weight": f"{proven_weight}",
            },
            cert_json["certificate"],
            coins,
        ]
        json.dump(verify_json, file, indent=4)
    file.close()
    print("Generate Certificate: ", round(time.time() - start, 2))
    # test.toDER()
    # test.toPEM()

    # print("verifyCertificate")
    # sigs_root = cert[0]
    # signed_weight = cert[1]
    # map_T = cert[2]
    # V = Verification(sigs_root, signed_weight, map_T, attester_root, message, proven_weight, hash)
    # if not V.verifyCertificate():
    #     print("Certificate is invalid")
    # else:
    #     print(f"Certificate is valid: {message}")
