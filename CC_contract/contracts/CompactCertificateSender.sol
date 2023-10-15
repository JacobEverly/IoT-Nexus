// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import {IRouterClient} from "@chainlink/contracts-ccip/src/v0.8/ccip/interfaces/IRouterClient.sol";
import {Client} from "@chainlink/contracts-ccip/src/v0.8/ccip/libraries/Client.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

// Uncomment this line to use console.log
// import "hardhat/console.sol";

using ECDSA for bytes32;

contract CompactCertificateSender {
    enum PayFeesIn {
        Native,
        Link
    }

    address public owner;
    // address immutable i_router;
    
    string constant private MSG_PREFIX = "\x19Ethereum Signed Message:\n32";
    mapping(address => string[]) public datas;
    mapping(address => bytes32) internal messages;
    mapping(address => bool) private _isValidSigner;
    uint private _threshold;
    uint256 public nonce;

    event StoreData(address user, string data);
    event SummarizeData(address user);
    event MessageSent(bytes32 messageId);
    event SetValidator(address newValidator);
    event RemoveValidator(address newValidator);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function.");
        _;
    }

    bool private _lock;
    modifier nonReentrant() {
        require(!_lock);
        _lock = true;
        _;
        _lock = false;
    }



    // constructor(address router, address[] memory _signers) {
    //     i_router = router;
    //     owner = msg.sender;
    //     _threshold = _signers.length; // or other threshold
    //     for (uint i = 0; i < _signers.length; i++) {
    //         _isValidSigner[_signers[i]] = true;
    //     }
    // }

    constructor(){
        owner = msg.sender;
    }

    receive() external payable {}

    function storeData (string memory data) external {
        datas[msg.sender].push(data);
        emit StoreData(msg.sender, data);
    }

    function getData (address user) external view returns (string[] memory) {
        return datas[user];
    }

    function clearData (address user) external {
        require(msg.sender == user, "Only data owner can delete data.");
        delete datas[user];
    }

    function summarizeData() external  {
        require(datas[msg.sender].length > 0, "No data stored");
        messages[msg.sender] =  keccak256(abi.encode(datas[msg.sender]));
        emit SummarizeData(msg.sender);
        
    }

    function getSummarizedMessage(address user) external view returns (bytes32 _summary) {
        return messages[user];
    }

    function clearDataSummary(address user) external {
        require(msg.sender == user, "Only data owner can delete data summary.");
        delete messages[user];
    }

    function setValidator(address validator) external onlyOwner(){
        _isValidSigner[validator] = true;
    }

    function removeValidator(address validator) external onlyOwner(){
        _isValidSigner[validator] = false;
    }

    function _processMessage(string memory message, uint256 _nonce) private pure returns (bytes32 _digest) {
        bytes memory encoded = abi.encode(message);
        _digest = keccak256(abi.encodePacked(encoded, _nonce));
        _digest = keccak256(abi.encodePacked(MSG_PREFIX, _digest));
    }

    function _verifyMultiSignature(string memory message, uint256 _nonce, bytes[] calldata _multiSignature) private {
        require(_nonce > nonce, "nonce already used");
        uint256 count = _multiSignature.length;
        require(count >= _threshold, "not enough signers");
        bytes32 digest = _processMessage(message, _nonce);

        address initSignerAddress;
        for(uint256 i = 0; i < count; i++) {
            bytes memory signature = _multiSignature[i];
            address signerAddress = ECDSA.recover(digest, signature );
            require( signerAddress > initSignerAddress, "possible duplicate" );
            require(_isValidSigner[signerAddress], "not part of consortium");
            initSignerAddress = signerAddress;
        }
        nonce = _nonce;

    }

    function sendMessage(string memory message, uint256 _nonce, bytes[] calldata _multiSignature) external nonReentrant() {
        _verifyMultiSignature(message, _nonce, _multiSignature);
        // send CCIP
    }
}





//         +------------+--------------+
//         | _txn       |     _nonce   |
//         +------------+--------------+
//                 |               |
//                 +---------------+
//                     | keccak256
// +------------+---------------+
// | MSG_PREFIX |   _hash       |   
// +------------+---------------+
//     |               |
//     +---------------+
//             | keccak256
//             +----------+         +--------------+
//             | _digest  |         |  signature   |   
//             +----------+         +--------------+                          
//                     |               |
//                     +---------------+
//                             | ECDSA.recover 
//                     +---------------+
//                     | signerAddress |
//                     +---------------+