import string
from random import SystemRandom
from math import log2, ceil
import time
from datetime import datetime
import json

from .keys import PrivateKey, PublicKey
from .eddsa import Eddsa
from .merkle import MerkleTree, verify_merkle_proof
from .utils import *
from .utils import _pemTemplate
from .hashes import int_to_hex, toDigit
from .elliptic_curves.baby_jubjub import BabyJubjubPoint


class Attestor:
    def __init__(
        self, private_key: PrivateKey = None, public_key: PublicKey = None, weight=None
    ):
        self.__private_key = private_key
        self.public_key = public_key
        self.weight = weight

    def getPrivateKey(self):
        return self.__private_key

    def setPublicKey(self, public_key):
        self.public_key = public_key

    def setWeight(self, weight):
        self.weight = weight

    def __repr__(self):
        return f"PK: {self.public_key}, SK: {self.__private_key}, Weight: {self.weight}"

    def __eq__(self, other) -> bool:
        return self.public_key == other.public_key and self.weight == other.weight

    def __str__(self):
        return f"{self.__private_key},{self.public_key},{self.weight}"


class Certificate:
    def __init__(
        self,
        message,
        hash,
        curve,
        sig_scheme,
        cert,
        hash_oid=[1, 3, 6, 1, 4, 1, 44625, 4, 3],
        curve_oid=[1, 3, 101, 112],
    ):
        self.message = message
        self.hash = hash
        self.curve = curve
        self.sig_scheme = sig_scheme
        self.sigs_root = cert[0]
        self.signed_weight = cert[1]
        self.map_T = cert[2]
        self.hash_oid = hash_oid
        self.curve_oid = curve_oid
        self.timestamp = datetime.today().strftime("%Y%m%d%H%M%S")

    def mapTtoStr(self):
        map_T_str = []
        for key, value in self.map_T.items():
            signature = value[0][0]
            data = {
                "index": f"{key}",
                "tree_size": f"{len(value[1])}",
                "signature": {
                    "r": [
                        f"{int_to_hex(signature.r.x)}",
                        f"{int_to_hex(signature.r.y)}",
                    ],
                    "s": f"{int_to_hex(signature.s)}",
                },
                "left_weight": f"{value[0][1]}",
                "sig_merkle_proof": [f"0x{v}" for v in value[1]],
                "public_key": [
                    f"{int_to_hex(value[2].public_key.point.x)}",
                    f"{int_to_hex(value[2].public_key.point.y)}",
                ],
                "attester_weight": f"{value[2].weight}",
                "attester_merkle_proof": [f"0x{v}" for v in value[3]],
            }
            map_T_str.append(data)
        return map_T_str

    def toJSON(self):
        digital_certificate = {
            # "version": 1,
            # "hashFunction": {
            #     "name": f"{self.hash}",
            #     "oid": self.hash_oid,
            # },
            # "signatureAlgorithm": {
            #     "curve": f"{self.curve}",
            #     "oid": self.curve_oid,
            #     "algorithm": f"{self.sig_scheme}",
            # },
            # "message": self.message,
            # "validity": {
            #     "notBefore": f"{self.timestamp}",
            #     "notAfter": f"{self.timestamp}"# "2023-01-01T00:00:00Z"
            # },
            "certificate": {
                "signature_root": f"0x{self.sigs_root}",
                "signed_weight": f"{self.signed_weight}",
                "map_t": self.mapTtoStr(),
            },
        }

        with open("certificate.json", "w") as file:
            json.dump(digital_certificate, file, indent=4)
        file.close()

        return digital_certificate

    def toDER(self):
        cert_dict = self.toJSON()
        version = encodePrimitive(DerFieldType.integer, cert_dict["version"])
        hash_function = encodeConstructed(
            encodePrimitive(DerFieldType.utf8String, cert_dict["hashFunction"]["name"]),
            encodePrimitive(
                DerFieldType.objectIdentifier, cert_dict["hashFunction"]["oid"]
            ),
        )
        signature_algorithm = encodeConstructed(
            encodePrimitive(
                DerFieldType.utf8String, cert_dict["signatureAlgorithm"]["curve"]
            ),
            encodePrimitive(
                DerFieldType.objectIdentifier, cert_dict["signatureAlgorithm"]["oid"]
            ),
            encodePrimitive(
                DerFieldType.utf8String, cert_dict["signatureAlgorithm"]["algorithm"]
            ),
        )

        message = encodePrimitive(DerFieldType.utf8String, cert_dict["message"])
        validity = encodeConstructed(
            encodePrimitive(DerFieldType.utcTime, cert_dict["validity"]["notBefore"]),
            encodePrimitive(DerFieldType.utcTime, cert_dict["validity"]["notAfter"]),
        )

        mapT = []
        for reveal in cert_dict["certificate"]["mapT"]:
            mapT.append(
                encodeConstructed(
                    encodePrimitive(DerFieldType.integer, reveal["index"]),
                    encodeConstructed(
                        encodePrimitive(
                            DerFieldType.octetString, reveal["signature"]["r"]
                        ),
                        encodePrimitive(
                            DerFieldType.octetString, reveal["signature"]["s"]
                        ),
                    ),
                    encodePrimitive(DerFieldType.integer, reveal["leftWeight"]),
                    encodePrimitive(
                        DerFieldType.utf8String, ",".join(reveal["sigMerkleProof"])
                    ),
                    encodePrimitive(DerFieldType.octetString, reveal["publicKey"]),
                    encodePrimitive(DerFieldType.integer, reveal["weights"]),
                    encodePrimitive(
                        DerFieldType.utf8String, ",".join(reveal["attesterMerkleProof"])
                    ),
                )
            )

        certificate = encodeConstructed(
            encodePrimitive(
                DerFieldType.octetString, cert_dict["certificate"]["signatureRoot"]
            ),
            encodePrimitive(
                DerFieldType.integer, cert_dict["certificate"]["signedWeight"]
            ),
            encodeConstructed(*mapT),
        )

        der = byteStringFromHex(
            encodeConstructed(
                version,
                hash_function,
                signature_algorithm,
                message,
                validity,
                certificate,
            )
        )

        with open("certificate.der", "wb") as file:
            file.write(der)
        file.close()

        return der

    def toPEM(self):
        der = self.toDER()
        pem = createPem(content=base64FromByteString(der), template=_pemTemplate)
        with open("certificate.pem", "w") as file:
            file.write(pem)
        file.close()
        return pem

    @classmethod
    def fromDER(self):
        pass

    @classmethod
    def fromPEM(self):
        pass


class CompactCertificate:
    def __init__(self, message, hash, curve, attesters=0):
        self.message = message
        self.hash = hash
        self.curve = curve
        self.attesters = [None] * attesters
        self.attester_tree = None
        self.signatures = [None] * len(self.attesters)
        self.signers = {}  # key: index in attesters, value: signature
        self.sigs_tree = None
        self.signed_weight = 0
        self.proven_weight = 0
        self.total_weight = 0
        self.map_T = {}

    def setAttestors(self):
        total_weight = 0
        for i in range(len(self.attesters)):
            sk = PrivateKey(self.curve)
            pk = sk.get_public_key()
            weight = SystemRandom().randrange(1, 1000)
            total_weight += weight

            self.attesters[i] = Attestor(sk, pk, weight)

        self.attesters = sorted(self.attesters, key=lambda x: x.weight, reverse=True)
        self.total_weight = total_weight
        self.proven_weight = round(0.51 * total_weight)

    def setAttestorsFromFile(self, filename="attesters.txt"):
        start = time.time()
        total_weight = 0
        with open(filename, "r") as file:
            for idx, attester in enumerate(file):
                if idx == len(self.attesters):
                    break
                attester = attester.split(",")
                sk = PrivateKey(self.curve, toDigit(attester[0]))
                pk = BabyJubjubPoint(toDigit(attester[1]), toDigit(attester[2]))
                pk = PublicKey(self.curve, pk)
                weight = int(attester[3])
                self.attesters[idx] = Attestor(sk, pk, weight)

                total_weight += weight

        self.attesters = sorted(self.attesters, key=lambda x: x.weight, reverse=True)
        self.total_weight = total_weight
        self.proven_weight = round(0.51 * total_weight)
        print("setAttestorsFromFile took: ", time.time() - start)

    def signMessage(self):
        """
        create signatures list with the following format: (signature, left_value, right_value)
        length of signatures list is the same as the length of attesters list
        atterters in signatures list that are not signers will have empty signature with L = R
        """
        start = time.time()
        while self.signed_weight < self.proven_weight or len(self.signers) < 2:
            i = SystemRandom().randrange(0, len(self.attesters))
            if i in self.signers:
                continue
            sk = self.attesters[i].getPrivateKey()
            signature = Eddsa.sign(
                self.message, sk, self.attesters[i].public_key, hash_fn=self.hash.run
            )

            if not Eddsa.verify(
                self.message,
                signature,
                self.attesters[i].public_key,
                hash_fn=self.hash.run,
            ):
                print("Signature is not valid")
                continue

            self.signers[i] = signature
            self.signed_weight += self.attesters[i].weight

        assert (
            len(self.signers) > 1
        ), "Not enough signatures, must be signed by at least 2 attestors"
        # self.signatures = sorted(self.signatures, key=lambda x: x[1], reverse=True)

        # create sigs list with same length as attesters list
        L = 0
        for i in range(len(self.signatures)):
            if i in self.signers:
                # signature, left_value, right_value to self.signatures
                R = L + self.attesters[i].weight
                sig = self.signers[i]
                self.signatures[i] = (sig, L, R)
            else:
                R = L
                self.signatures[i] = ("", L, R)
            L = R
        print("signing time: ", time.time() - start)

    def verifySignatures(self):
        for i in range(len(self.attesters)):
            pk = self.attesters[i].public_key
            signature = self.signatures[i]
            if not Eddsa.verify(self.message, signature, pk, hash_fn=self.hash.run):
                return False
        return True

    def buildAttesterTree(self):
        """
        Create merkle tree including attestors public keys
        """
        # pks = [attester.public_key.toString() for attester in self.attesters]
        pks = [attester.public_key.toString() for attester in self.attesters]
        self.attester_tree = MerkleTree(pks, hash_fn=self.hash.run)

    def buildSignTree(self):
        """
        Create merkle tree including Witness (Signed message by SK) and attestors range which is their spot in the provenweight
        """
        signatures = []
        for signature in self.signatures:
            signatures.append(str(signature))  # signature, left_value, right_value

        self.sigs_tree = MerkleTree(signatures, hash_fn=self.hash.run)

    def createMap(self):
        """
        Create a map(T) of the attestors that signed the message for verification
        """
        # k = 64  # we dont't know what k and q is yet
        # q = 64
        # self.num_reveals = ceil((k + q) / log2(self.signed_weight / self.proven_weight))
        self.num_reveals = 132
        sigs_root = self.sigs_tree.get_root()
        attester_root = self.attester_tree.get_root()
        for j in range(self.num_reveals):
            hin = (
                j,
                toDigit(sigs_root),
                self.proven_weight,
                toDigit(self.hash.run(self.message).hexdigest()),
                toDigit(attester_root),
            )
            coin = (
                int.from_bytes(self.hash.run(sum(hin)).digest(), "big")
                % (self.signed_weight - 1)
                + 1
            )
            idx = self.intToIdx(coin)

            assert idx != -1, "Coin is not in range"
            if idx not in self.map_T:
                self.map_T[idx] = (
                    (self.signatures[idx][0], self.signatures[idx][1]),  # with R value
                    self.sigs_tree.get_proof(idx),  # merkle proof of signature
                    self.attesters[idx],  # TODO this shouldn't include private key
                    self.attester_tree.get_proof(
                        idx
                    ),  # merkle proof of attester?? not sure is all attestors or just the one that signed, refer p5 step 6
                )

    def intToIdx(self, coin):
        """
        Returns the index of the signature that contains the coin, binary search
        """
        low = 0
        high = len(self.signatures) - 1
        while low <= high:
            mid = (low + high) // 2
            L = self.signatures[mid][1]
            R = self.signatures[mid][2]
            if L < coin <= R and L != R:
                return mid

            if coin > R:
                low = mid + 1
            elif coin <= L:
                high = mid - 1

        return -1

    def getCertificate(self):
        sigs_root = self.sigs_tree.get_root()
        attester_root = self.attester_tree.get_root()
        return (
            attester_root,
            self.message,
            self.proven_weight,
            (sigs_root, self.signed_weight, self.map_T),  # The map T in the paper
            self.num_reveals,
        )


class Verification:
    # attester_tree, message, proven_weight, sign_weight, map T
    def __init__(
        self,
        sigs_root,
        signed_weight,
        map_T,
        attester_root,
        message,
        proven_weight,
        hash,
    ):
        self.sigs_root = sigs_root
        self.signed_weight = signed_weight
        self.map_T = map_T
        self.message = message
        self.proven_weight = proven_weight
        self.attester_root = attester_root
        self.hash = hash

    def verifyCertificate(self):
        start = time.time()
        # Make sure signed weight is greater than proven weight on cerificate
        if self.signed_weight < self.proven_weight:
            return False

        # Checks to make sure data is valid on certificate
        for idx, reveal in self.map_T.items():
            signature = reveal[0][0]
            L = reveal[0][1]
            sigs_proof = reveal[1]
            attester = reveal[2]
            attester_proof = reveal[3]

            # Make sure that paths are valid for given index in respect to Sig Tree
            if not verify_merkle_proof(
                idx, sigs_proof[:], self.sigs_root, self.hash.run
            ):
                print("sign_proof invalid")
                return False

            # check vector commitments are valid for mapping
            if not verify_merkle_proof(
                idx, attester_proof[:], self.attester_root, self.hash.run
            ):
                print("attester_proof invalid")
                return False

            # Make sure signature on M is a valid key in ground truth
            public_key = attester.public_key
            if not Eddsa.verify(
                self.message, signature, public_key, hash_fn=self.hash.run
            ):
                print("signature invalid")
                return False

            if not self.verifyCoin(
                signature, L, sigs_proof[:], attester, attester_proof
            ):
                print("no coin get match this signature")
                return False
        print("time to verify certificate", time.time() - start)
        return True

    def verifyCoin(self, signature, L, sigs_proof, attester, attester_proof):
        # k = 64  # we dont't know what k and q is yet
        # q = 64
        # num_reveals = ceil((k + q) / log2(self.signed_weight / self.proven_weight))
        num_reveals = 132
        for j in range(num_reveals):
            # hin = (
            #     j,
            #     self.sigs_root,
            #     self.proven_weight,
            #     self.message,
            #     self.attester_root,
            # )
            hin = (
                j,
                toDigit(self.sigs_root),
                self.proven_weight,
                toDigit(self.hash.run(self.message).hexdigest()),
                toDigit(self.attester_root),
            )
            coin = (
                int.from_bytes(self.hash.run(sum(hin)).digest(), "big")
                % (self.signed_weight - 1)
                + 1
            )

            for pos, t in self.map_T.items():
                t_sig = t[0][0]
                t_L = t[0][1]
                t_sigs_proof = t[1]
                t_attester = t[2]
                t_attester_proof = t[3]
                if t_L < coin <= (t_L + t_attester.weight):
                    if (
                        t_sig == signature
                        and t_L == L
                        and t_sigs_proof == sigs_proof
                        and t_attester == attester
                        and t_attester_proof == attester_proof
                    ):
                        return True
                    else:
                        continue

        return False
