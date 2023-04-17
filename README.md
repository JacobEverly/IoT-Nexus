# IoT Nexus (Work in Progress)

This is an implementation of [Efficiently Verifying IoT State in Web3:A Succinct Proof Approach for Scalable and Transparent Applications](https://github.com/JacobEverly/IoT-Nexus/files/11255572/Independent_Research__CCs.7.pdf), we provide a library called py_cc. 

py_cc includes the Poseidon Hash function, Baby Jubjub Elliptic Curve, EdDSA, and a Merkle Tree implementation with Least Significant Bits (LSB) indexing - all necessary for constructing Compact Certificates (CCs). 

To verify the CCs, we use the efficient verification tool Zokrates, and a JavaScript version is available for seamless integration with front-end systems. We adopt Groth16 as our proof scheme.

Our library streamlines the process of constructing CCs and verifying their authenticity, making it an ideal resource for developers seeking to develop secure, transparent, and scalable IoT applications. We welcome your feedback and contributions to our library.
[Slide deck](https://docs.google.com/presentation/d/15pQ7v32UwxOXyHta_z7LKtmoQuxZqJMF870_tQHAGBo/edit#slide=id.g22e5be66688_0_20)


## Setup System

### Project Frontend
Follow the instruction in [IoT Nexus Frontend](https://github.com/samhithatarra/Attestor-Frontend).

### Project Backend

1. Create enviroment
```cmd
conda create -n {env} python=3.9
conda activate {env}
```

2. Install Python dependencies
```cmd
pip install -r requirement.txt
pip install -Ue .
```

3. Install ZoKkrates
Follow the [official Document](https://zokrates.github.io/introduction.html)

4. Install ZokratesJS
```cmd
cd zokratesjs
npm i
```

## Execute Program(local)
**Backend only**
```
python main.py -n {number of attesters} -m {message}
cd zokrates && node index.js && cd ..
```

**Setup localhost**
```
FLASK_APP=routes.py flask run
```

## Example
```python
import argparse
import json
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

    num = args.num
    message = args.message
    
    hash_fn = Poseidon(
        prime_254,
        128,
        5,
        3,
        full_round=8,
        partial_round=57,
        mds_matrix=matrix_254_3,
        rc_list=round_constants_254_3,
    )
    CC = CompactCertificate(message, hash_fn, curve, num)

    # setup/collect attesters (only for testing)
    CC.setAttestors()

    # attesters sign message
    CC.signMessage()

    # build merkle trees
    CC.buildAttesterTree()
    CC.buildSignTree()
    CC.createMap()

    # get certificate (to be optimized)
    attester_root, message, proven_weight, cert, coins = CC.getCertificate()

    # export compact certificate
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
     
    # verify compact certificate (same process as zokrates)
    sigs_root = cert[0]
    signed_weight = cert[1]
    map_T = cert[2]
    V = Verification(sigs_root, signed_weight, map_T, attester_root, message, proven_weight, hash)
    if not V.verifyCertificate():
        print("Certificate is invalid")
    else:
        print(f"Certificate is valid: {message}")
```


## Additional Info
**Zokrates Commands**
```cmd
# Compile
zokrates compile -i {file name}.zok

# Setup
zokrates setup -i

# Compute Witness
zokrates compute-witness --abi -i --stdin --verbose < {file name}.json

# Generate Proof
zokrates generate-proof -i

# Verify Proof
zokrates verify-proof -i

# Export Verifier
zokrates export-verifier -i
```

**Create and switch branch**
```cmd
# Create branch
git branch {branch name}

# Switch branch
git checkout {branch name}

# Push to branch
git push -u origin {branch name} # for the first time
git push # for afterwards

# synchronize(rebase) with main branch
git fetch
git rebase main

# Delete branch
git branch -d {branch name}
git checkout main
```
Then do pull request for merging to main branch

**Git push**
```cmd
git add {changed files}
git commit -m "{description}"
git push
```

## TODO List
- [x] Posedidon
- [x] Baby JubJub
- [x] Signature Scheme
- [x] Merkle Tree
- [x] Weight Generation
- [x] Validtor Selection
- [x] Proof System
- [ ] Optimization

