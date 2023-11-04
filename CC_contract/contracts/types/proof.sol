// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.19;

struct Proof {
    string[] a;
    string[][] b;
    string[] c;
}

struct ZKProof {
    string scheme;
    string curve;
    Proof proof;
    string[] inputs;
}
