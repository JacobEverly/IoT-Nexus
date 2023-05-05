# py_cc Documentation

## Structure
```
${ROOT}
    |-- elliptic_curve
    |   |-- __init__.py
    |   |-- baby_jubjub.py
    |-- hashes
    |   |-- parameters.py
    |   |-- poseidon.py
    |   |-- sah256.py
    |   |-- utils.py
    |-- __init__.py
    |-- certificate.py
    |-- ecdsa.py
    |-- eddsa.py
    |-- utils.py
    |-- keys.py
    |-- merkle.py
    |-- signature.py
```

## Trace Code
1. Starting with certificate.py, it include class Certificate, CompactCertificate, Verfication and Attester
2. merkle.py
3. Then hashes folder
4. elliptic_curve folder
5. keys.py, eddsa.py, signatures.py