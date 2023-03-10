import pytest
from py_cc.elliptic_curves import BabyJubjubPoint

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