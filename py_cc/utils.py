import random
import hashlib
from sys import version_info as pyVersion
from binascii import hexlify, unhexlify
from base64 import b64encode, b64decode

# Create Random Oracle that tells us the subrange that the prover should select a tree from


def random_oracle(merkle_root_hash, modulus):
    nonce = random.getrandbytes(8)
    # Hash the Merkle root hash and nonce value together
    h = hashlib.sha256(merkle_root_hash + nonce.to_bytes(8, "big")).digest()

    # Interpret the hash value as a number in the range from 0 to the sum of the weights
    random_number = int.from_bytes(h, "big") % modulus
    return random_number


class DerFieldType:

    boolean = "boolean"
    integer = "integer"
    bitString = "bitString"
    octetString = "octetString"
    null = "null"
    objectIdentifier = "objectIdentifier"
    utf8String = "utf8String"
    printableString = "printableString"
    utcTime = "utcTime"
    sequence = "sequence"
    set = "set"
    oidContainer = "oidContainer"
    publicKeyPointContainer = "publicKeyPointContainer"


_hexTagToType = {
    "01": DerFieldType.boolean,
    "02": DerFieldType.integer,
    "03": DerFieldType.bitString,
    "04": DerFieldType.octetString,
    "05": DerFieldType.null,
    "06": DerFieldType.objectIdentifier,
    "0C": DerFieldType.utf8String,
    "13": DerFieldType.printableString,
    "17": DerFieldType.utcTime,
    "30": DerFieldType.sequence,
    "31": DerFieldType.set,
    "a0": DerFieldType.oidContainer,
    "a1": DerFieldType.publicKeyPointContainer,
}
_typeToHexTag = {v: k for k, v in _hexTagToType.items()}

_pemTemplate = """
-----BEGIN EC PRIVATE KEY-----
{content}
-----END EC PRIVATE KEY-----
"""


def createPem(content, template):
    lines = [
        content[start:start + 64]
        for start in range(0, len(content), 64)
    ]
    return template.format(content="\n".join(lines))


def encodeConstructed(*encodedValues):
    return encodePrimitive(DerFieldType.sequence, "".join(encodedValues))


def encodePrimitive(tagType, value):
    if tagType == DerFieldType.integer:
        value = _encodeInteger(value)
    if tagType == DerFieldType.objectIdentifier:
        value = oidToHex(value)
    if tagType == DerFieldType.utf8String:
        value = _encodeUTF8String(value)
    return "{tag}{size}{value}".format(tag=_typeToHexTag[tagType], size=_generateLengthBytes(value), value=value)


def _generateLengthBytes(hexadecimal):
    size = len(hexadecimal) // 2
    length = hexFromInt(size)
    # checks if first bit of byte should be 0 (a.k.a. short-form flag)
    if size < 128:
        return length.zfill(2)
    # +128 sets the first bit of the byte as 1 (a.k.a. long-form flag)
    lengthLength = 128 + len(length) // 2
    return hexFromInt(lengthLength) + length


def _encodeInteger(number):
    hexadecimal = hexFromInt(abs(number))
    if number < 0:
        bitCount = 4 * len(hexadecimal)
        twosComplement = (2 ** bitCount) + number
        return hexFromInt(twosComplement)
    bits = bitsFromHex(hexadecimal[0])
    if bits[0] == "1":  # if first bit was left as 1, number would be parsed as a negative integer with two's complement
        hexadecimal = "00" + hexadecimal
    return hexadecimal


def _encodeUTF8String(string):
    return string.encode('utf-8').hex()


def oidFromHex(hexadecimal):
    firstByte, remainingBytes = hexadecimal[:2], hexadecimal[2:]
    firstByteInt = intFromHex(firstByte)
    oid = [firstByteInt // 40, firstByteInt % 40]
    oidInt = 0
    while len(remainingBytes) > 0:
        byte, remainingBytes = remainingBytes[0:2], remainingBytes[2:]
        byteInt = intFromHex(byte)
        if byteInt >= 128:
            oidInt = (128 * oidInt) + (byteInt - 128)
            continue
        oidInt = (128 * oidInt) + byteInt
        oid.append(oidInt)
        oidInt = 0
    return oid


def oidToHex(oid):
    hexadecimal = hexFromInt(40 * oid[0] + oid[1])
    for number in oid[2:]:
        hexadecimal += _oidNumberToHex(number)
    return hexadecimal


def _oidNumberToHex(number):
    hexadecimal = ""
    endDelta = 0
    while number > 0:
        hexadecimal = hexFromInt((number % 128) + endDelta) + hexadecimal
        number //= 128
        endDelta = 128
    return hexadecimal or "00"


def hexFromInt(number):
    hexadecimal = "{0:x}".format(number)
    if len(hexadecimal) % 2 == 1:
        hexadecimal = "0" + hexadecimal
    return hexadecimal


def intFromHex(hexadecimal):
    return int(hexadecimal, 16)


def hexFromByteString(byteString):
    return safeHexFromBinary(byteString)


def byteStringFromHex(hexadecimal):
    return safeBinaryFromHex(hexadecimal)


def numberFromByteString(byteString):
    return intFromHex(hexFromByteString(byteString))


def base64FromByteString(byteString):
    return toString(b64encode(byteString))


def byteStringFromBase64(base64String):
    return b64decode(base64String)


def bitsFromHex(hexadecimal):
    return format(intFromHex(hexadecimal), 'b').zfill(4 * len(hexadecimal))


def toString(string, encoding="utf-8"):
    return string.decode(encoding)


def toBytes(string, encoding="utf-8"):
    return string.encode(encoding)


def safeBinaryFromHex(hexadecimal):
    if len(hexadecimal) % 2 == 1:
        hexadecimal = "0" + hexadecimal
    return unhexlify(hexadecimal)


def safeHexFromBinary(byteString):
    return toString(hexlify(byteString))
