// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import {ZKProof} from "./types/proof.sol";
import {CCIPReceiver} from "@chainlink/contracts-ccip/src/v0.8/ccip/applications/CCIPReceiver.sol";
import {Client} from "@chainlink/contracts-ccip/src/v0.8/ccip/libraries/Client.sol";

contract CompactCertificateReceiver is CCIPReceiver {
    event MessageReceived(
        bytes32 messageId,
        uint64 sourceChainSelector,
        address sender,
        string proof
    );

    mapping(bytes32 => string) public proofs;

    constructor(address router) CCIPReceiver(router) {}

    function _ccipReceive(
        Client.Any2EVMMessage memory message
    ) internal override {
        bytes32 messageId = message.messageId;
        uint64 sourceChainSelector = message.sourceChainSelector;
        address sender = abi.decode(message.sender, (address));
        string memory proof = abi.decode(message.data, (string));
        proofs[messageId] = proof;

        emit MessageReceived(messageId, sourceChainSelector, sender, proof);
    }
}
