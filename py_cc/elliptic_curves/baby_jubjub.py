import collections
import random
from galois import GF

EllipticCurve = collections.namedtuple('EllipticCurve', 'name p a d G B h l n length')

curve = EllipticCurve(
    'baby_jubjub',
    # Field characteristic.
    p = 21888242871839275222246405745257275088548364400416034343698204186575808495617,
    # Curve coefficients.
    a = 168700,
    d = 168696,
    # Generate point.
    G = (995203441582195749578291179787384436505546430278305826713579947235728471134,
       5472060717959818805561601436314318772137091100104008585924551046643952123905),
    # Base point.
    B = (5299619240641551281634865583518297030282874472190772894086521144482721001553,
         16950150798460657717958625567821834550301663161624707787222815936182638968203),
    # h is called subgroup cofactor and l is a prime number of 251 bits.
    h = 8,
    # l is a prime number of 251 bits.
    l = 2736030358979909402780800718157159386076813972158567259200215660948447373041,
    # Subgroup order = h * l.
    n = 8 * 2736030358979909402780800718157159386076813972158567259200215660948447373041,
    length = 1 + len("%x" % (8 * 2736030358979909402780800718157159386076813972158567259200215660948447373041)) // 2
)

# FQ = GF(curve.p)

def mulmod(a, b, m):
    return (a * b) % m

def addmod(a, b, m):
    return (a + b) % m

def submod(a, b, m):
    aNN = a
    if a <= b:
        aNN += m
    return addmod(aNN - b, 0, m)

def inverse(a, m):
    # Since m = prime we have: a^-1 = a^(m - 2) (mod m)
    return pow(a, m - 2, m)

class BabyJubjubPoint:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    # Define addition operation on the curve
    def __add__(self, other):
        if not isinstance(other, BabyJubjubPoint):
            raise TypeError("Unsupported operand type for +")
        if self == BabyJubjubPoint(0, 0):
            return other
        if other == BabyJubjubPoint(0, 0):
            return self
        # if self.x == other.x:
        #     if (self.y + other.y) % curve.p == 0:
        #         return BabyJubjubPoint(None, None)
        #     else:
        #         return self.__double__()
        

        x1x2 = mulmod(self.x, other.x, curve.p)
        y1y2 = mulmod(self.y, other.y, curve.p)
        dx1x2y1y2 = mulmod(curve.d, mulmod(x1x2, y1y2, curve.p), curve.p)
        x3Num = addmod(mulmod(self.x, other.y, curve.p), mulmod(self.y, other.x, curve.p), curve.p)
        y3Num = submod(y1y2, mulmod(curve.a, x1x2, curve.p), curve.p)

        x3 = mulmod(x3Num, inverse(addmod(1, dx1x2y1y2, curve.p), curve.p), curve.p)
        y3 = mulmod(y3Num, inverse(submod(1, dx1x2y1y2, curve.p), curve.p), curve.p)

        return BabyJubjubPoint(x3, y3)

    # Define multiplication operation on the curve
    def __mul__(self, d):
        if not isinstance(d, int):
            raise TypeError("Unsupported operand type for *")
        if d < 0 or d >= curve.n:
            raise ValueError("Invalid scalar value")
        if d == 0:
            return BabyJubjubPoint(0, 0)
        if d == 1:
            return self
        
        remaining = d

        _p = BabyJubjubPoint(self.x, self.y)
        _a = BabyJubjubPoint(0, 0)

        while remaining > 0:
            if remaining & 1:
                _a = _a + _p

            _p = _p.double()
            remaining >>= 1
        
        return _a

    def __rmul__(self, d):
        return self.__mul__(d)

    # Define negation operation on the curve
    def __neg__(self):
        return BabyJubjubPoint(self.x, curve.p - self.y)

    # Define double operation on the curve
    def double(self):
        return self.__add__(self)
    
    def isOnCurve(self):
        xSq = mulmod(self.x, self.x, curve.p)
        ySq = mulmod(self.y, self.y, curve.p)
        lhs = addmod(mulmod(curve.a, xSq, curve.p), ySq, curve.p)
        rhs = addmod(1, mulmod(mulmod(curve.d, xSq, curve.p), ySq, curve.p), curve.p)
        return submod(lhs, rhs, curve.p) == 0
    
    def isAtInfinity(self):
        return self.y == 0

    def __eq__(self, other):
        if not isinstance(other, BabyJubjubPoint):
            raise TypeError("Unsupported operand type for *")
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        x = "x: {}".format(self.x)
        y = "y: {}".format(self.y)
        return x + "\t" + y
    
    def __str__(self):
        x = "x: {}".format(self.x)
        y = "y: {}".format(self.y)
        return x + "\t" + y


GeneratePoint = BabyJubjubPoint(curve.G[0], curve.G[1])

if __name__ == "__main__":
    p1 = BabyJubjubPoint(17777552123799933955779906779655732241715742912184938656739573121738514868268, 2626589144620713026669568689430873010625803728049924121243784502389097019475)
    p2 = BabyJubjubPoint(16540640123574156134436876038791482806971768689494387082833631921987005038935, 20819045374670962167435360035096875258406992893633759881276124905556507972311)
    
    sum = BabyJubjubPoint(7916061937171219682591368294088513039687205273691143098332585753343424131937, 14035240266687799601661095864649209771790948434046947201833777492504781204499)
    assert p1 + p2 == sum, "Addition operation is not correct"

    double = BabyJubjubPoint(6890855772600357754907169075114257697580319025794532037257385534741338397365, 4338620300185947561074059802482547481416142213883829469920100239455078257889)
    assert p1.double() == double, "Double operation is not correct"

    p1 = BabyJubjubPoint(0, 1)
    p2 = BabyJubjubPoint(0, 1)
    assert p1 + p2 == BabyJubjubPoint(0, 1), "Doubling the identity operation is not correct"
    assert p1.isOnCurve(), "Point should be on the curve"

    p1 = BabyJubjubPoint(1, 0)
    assert not p1.isOnCurve(), "Point should not be on the curve"

    base = BabyJubjubPoint(curve.B[0], curve.B[1])
    gen = BabyJubjubPoint(curve.G[0], curve.G[1])
    mul = gen * 8
    assert mul == base, "Base point should be 8 times Generate point, but \n{}".format(mul)

    mul = 8 * gen
    assert mul == base, "Base point should be 8 times Generate point, but \n{}".format(mul)

    order = base * curve.l
    assert order == BabyJubjubPoint(0, 1), "Base point order should be BabyJubjubPoint(0, 1), but \n{}".format(order)