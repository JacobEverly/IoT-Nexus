'use strict';
// import { initialize } from "zokrates-js";
// import express from "express";

// import certificate from './verify.json' assert { type: 'json' };

// const app = express()
// const port = 8000

// app.post('/api/verify', (req, res) => {
//     const proof = runProof(req.certificate);
//     res.send(proof)
// })

// app.listen(port, () => {
//     console.log(`Example app listening on port ${port}`)
// })
const fs = require('fs');
let rawdata = fs.readFileSync('verify.json');
let certificate = JSON.parse(rawdata);
// console.log(certificate);

async function runProof(certificate) {
    let { initialize } = await import("zokrates-js");
    return initialize().then((zokratesProvider) => {
        let MAP_SIZE = certificate[2].map_t.length;
        let PROOF_SIZE = certificate[2].map_t[0].sig_merkle_proof.length;
        const source = `
        from "hashes/poseidon/poseidon" import ark;
        from "hashes/poseidon/poseidon" import sbox;
        from "hashes/poseidon/poseidon" import mix;
        from "hashes/poseidon/poseidon" import POSEIDON_C;
        from "hashes/poseidon/poseidon" import POSEIDON_M;
        
        import "ecc/edwardsScalarMult" as scalarMult;
        import "ecc/edwardsAdd" as add;
        import "ecc/edwardsOnCurve" as onCurve;
        import "ecc/edwardsOrderCheck" as orderCheck;
        from "ecc/babyjubjubParams" import BabyJubJubParams;
        import "utils/pack/bool/nonStrictUnpack256" as nonStrictUnpack256bool;
        import "utils/pack/bool/unpack256" as unpack256bool;
        import "utils/casts/u32_to_field" as cast32toField;
        import "utils/casts/field_to_u32" as castFieldto32;
        
        const u32 MAP_SIZE = ${MAP_SIZE};
        const u32 PROOF_SIZE = ${PROOF_SIZE};
        const u32 REVEAL_NUM = 132;
        
        struct Message {
            field message;
        }
        
        struct Commitment {
            field attester_root;
            u32 proven_weight;
        }
        
        
        struct Signature {
            field[2] r;
            field s;
        }
        
        struct MapT {
            u32 index;
            u32 tree_size;
            Signature signature;
            u32 left_weight;
            field[PROOF_SIZE] sig_merkle_proof;
            field[2] public_key;
            u32 attester_weight;
            field[PROOF_SIZE] attester_merkle_proof;
        }
        
        struct Certificate {
            field signature_root;
            u32 signed_weight;
            MapT[MAP_SIZE] map_t;
        }
        
        struct Coin {
            u32 coin;
            u32 idx;
        }
        
        const BabyJubJubParams BABYJUBJUB_PARAMS = BabyJubJubParams {
            // Order of the curve for reference: 21888242871839275222246405745257275088614511777268538073601725287587578984328
            JUBJUB_C: 8, // Cofactor
            JUBJUB_A: 168700, // Coefficient A
            JUBJUB_D: 168696, // Coefficient D
        
            // Montgomery parameters
            MONT_A: 168698,
            MONT_B: 1,
        
            // Point at infinity
            INFINITY: [0, 1],
        
            // Generator
            Gu: 995203441582195749578291179787384436505546430278305826713579947235728471134,
            Gv: 5472060717959818805561601436314318772137091100104008585924551046643952123905
        };
        
        def poseidon(field msg) -> field {
            u32 t = 3;
            u32 alpha = 3;
            u32 full = 8;
            u32 partial = 57;
            field[3] mut state = [msg, 1, 2];
        
            u32 mut round = 0;
        
            field[497]  constants = POSEIDON_C[t - 2];
            field[7][7] mds = POSEIDON_M[t - 2];
        
            for u32 round in 0..full + partial {
                state = ark(state, constants, round * t);
                state = sbox(state, full, partial, round);
                state = mix(state, mds);
            }
        
            return state[0];
        }
        
        
        def create_commitment<N>(field commitment, u32 index, field[N] proof) -> bool {
            field mut current_hash = proof[0];
            u32 mut shift = N;
            for u32 i in 1..N {
                shift = shift - 1;
                current_hash = if (index & (1 << (shift))) == 0 {
                    poseidon(current_hash + proof[i])
                } else {
                    poseidon(proof[i] + current_hash)
                };
            }
            return commitment == current_hash;
        }
        
        def verify_merkle_proof<N>(field commitment, u32 index, field[N] proof) -> bool {
            assert(N > 0);
        
            bool res = if N < 2 {
                commitment == proof[0]
            } else {
                create_commitment(commitment, index, proof)
            };
            return res;
        }
        
        def verifyEdDSA(field message, Signature signature, field[2] public_key, BabyJubJubParams context) -> bool {
            field[2] G = [context.Gu, context.Gv];
            field[2] R = signature.r;
            field S = signature.s;
        
            // assert(onCurve(R, context)); // throws if R is not on curve
            // assert(orderCheck(R, context));
        
            field k = poseidon(R[1] + public_key[1] + message);
            bool[256] sBits = unpack256bool(S);
            field[2] lhs = scalarMult(sBits, G, context);
        
            bool[256] kRAM = unpack256bool(k);
            field[2] AhRAM = scalarMult(kRAM, public_key, context);
            field[2] rhs = add(R, AhRAM, context);
        
            bool res = rhs[0] == lhs[0] && rhs[1] == lhs[1];
            return res;
        }
        def verify_coin<N>(
            Coin[REVEAL_NUM] reveals,
            MapT ver_t,
            MapT[N] map_t
        ) -> bool {
            bool mut res = true;
            for u32 i in 0..REVEAL_NUM {
                u32 coin = reveals[i].coin;
                u32 idx = reveals[i].idx;
                MapT t = map_t[idx];
                res = if (
                    ver_t.signature ==t.signature &&
                    ver_t.left_weight == t.left_weight &&
                    ver_t.public_key == t.public_key &&
                    ver_t.attester_weight == t.attester_weight &&
                    ver_t.sig_merkle_proof == t.sig_merkle_proof &&
                    ver_t.attester_merkle_proof == t.attester_merkle_proof && 
                    ver_t.left_weight < coin &&
                    coin <= ver_t.left_weight + ver_t.attester_weight
                ) {
                    true
                } else {
                    res
                };
            }
            return res;
        }
        
        def main(
            Message msg, 
            Commitment commitment, 
            private Certificate certificate, //private variable must be used in main function
            private Coin[REVEAL_NUM] reveals
            ) -> bool {
                bool mut res = false;
        
                // check signed weight overpass the threshold
                res = certificate.signed_weight < commitment.proven_weight? false : true;
                assert(res);
        
                for u32 i in 0..MAP_SIZE {
                    // verify merkle path
                    MapT t = certificate.map_t[i];
                    res = verify_merkle_proof(certificate.signature_root, t.index, t.sig_merkle_proof);
                    assert(res);
                    res = verify_merkle_proof(commitment.attester_root, t.index, t.attester_merkle_proof);
                    assert(res);
        
                    // verify signature
                    res = verifyEdDSA(msg.message, t.signature, t.public_key, BABYJUBJUB_PARAMS);
                    assert(res);
                    
                    // verify coin
                    res = verify_coin(reveals, t, certificate.map_t);
                    assert(res);
                }
        
                return res;
            }
        
        `;

        // compilation
        const artifacts = zokratesProvider.compile(source);

        // computation
        const { witness, output } = zokratesProvider.computeWitness(artifacts, certificate);
        console.log(output)
        // run setup
        const keypair = zokratesProvider.setup(artifacts.program);
        // generate proof
        const proof = zokratesProvider.generateProof(
            artifacts.program,
            witness,
            keypair.pk
        );
        let data = JSON.stringify(proof, null, 4);
        // export solidity verifier
        const verifier = zokratesProvider.exportSolidityVerifier(keypair.vk);

        // or verify off-chain
        const isVerified = zokratesProvider.verify(keypair.vk, proof);
        console.log(isVerified);
        if (!isVerified) {
            data = JSON.stringify({ message: 'Proof is not verified' }, null, 4);
        }
        fs.writeFileSync('proof.json', data);
        return isVerified;
    });
}

runProof(certificate);