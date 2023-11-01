// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import {IRouterClient} from "@chainlink/contracts-ccip/src/v0.8/ccip/interfaces/IRouterClient.sol";
import {Client} from "@chainlink/contracts-ccip/src/v0.8/ccip/libraries/Client.sol";
import {ZKProof} from "./types/proof.sol";
import {SignMessage} from "./types/message.sol";

contract CompactCertificateSender {
    struct Validator {
        address walletAddress;
        string eddsaPublicKey;
        bool isValid;
    }

    address immutable i_router;

    address public owner;
    uint256 public totalValidators;
    uint256 public totalStakes;
    uint public stakeAmount;
    Validator[] public validators;

    mapping(address => string[]) public datas;
    mapping(address => string) internal messages;
    mapping(address => uint256) private validatorIndex;
    mapping(address => mapping(string => SignMessage)) public messageSigned;
    mapping(address => mapping(string => string)) public signatures;
    mapping(address => uint256) public stakes;
    uint256 public nonce;

    error NotEnoughBalance(uint256 currentBalance, uint256 calculatedFees);
    error SignatureNotEnough(uint signatures, uint totalValidators);

    event SetStakeAmount(uint256 amount);
    event SetValidator(address indexed newValidator, string eddsaPublicKey);
    event RemoveValidator(address indexed newValidator);
    event Slash(address indexed validator, uint256 amount);
    event StoreData(address user, string data);
    event SummarizeData(address user);
    event CreateSignature(
        address indexed validator,
        string indexed message,
        string signature,
        SignMessage decision
    );
    event MessageSent(bytes32 messageId);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function.");
        _;
    }

    modifier onlyValidator() {
        uint256 index = validatorIndex[msg.sender];
        require(
            validators[index - 1].isValid,
            "Only validator can call this function."
        );
        _;
    }

    bool private _lock;
    modifier nonReentrant() {
        require(!_lock);
        _lock = true;
        _;
        _lock = false;
    }

    constructor(address router, uint256 amount) {
        i_router = router;
        owner = msg.sender;
        stakeAmount = amount;
    }

    receive() external payable {}

    function setStakeAmount(uint256 amount) external onlyOwner {
        stakeAmount = amount;
        emit SetStakeAmount(amount);
    }

    function setValidator(
        address validator,
        string memory eddsaPublicKey
    ) external payable {
        uint256 index = validatorIndex[validator];
        // require(
        //     index > 0 && !validators[index - 1].isValid,
        //     "Validator already exists"
        // );
        require(msg.value >= stakeAmount, "Insufficient stake amount");

        if (index > 0) {
            validators[index - 1].isValid = true;
        } else {
            validators.push(Validator(msg.sender, eddsaPublicKey, true));
            validatorIndex[validator] = validators.length;
        }
        stakes[validator] = msg.value;
        totalValidators++;
        totalStakes += msg.value;
        emit SetValidator(validator, eddsaPublicKey);
    }

    function removeValidator(address validator) external onlyValidator {
        _removeValidator(validator);
        // _withdrawStake();
    }

    function _removeValidator(address validator) internal {
        uint256 index = validatorIndex[validator];
        validators[index - 1].isValid = false;
        totalValidators--;
        payable(validator).transfer(stakes[validator]);
        emit RemoveValidator(validator);
    }

    function getValidator(
        address validator
    ) external view returns (Validator memory) {
        uint256 index = validatorIndex[validator];
        return validators[index - 1];
    }

    // function _withdrawStake() internal {
    //     require(stakes[msg.sender] > 0, "No stake to withdraw");
    //     uint256 amount = stakes[msg.sender];
    //     stakes[msg.sender] = 0;
    //     payable(msg.sender).transfer(amount);
    // }

    function _slash(address validator, uint amount) internal {
        if (stakes[validator] >= amount) {
            stakes[validator] -= amount;
            totalStakes -= amount;
        } else {
            totalStakes -= stakes[validator];
            stakes[validator] = 0;
            _removeValidator(validator);
        }
        emit Slash(validator, amount);
    }

    function storeData(string memory data) external {
        datas[msg.sender].push(data);
        emit StoreData(msg.sender, data);
    }

    function getData(address user) external view returns (string[] memory) {
        return datas[user];
    }

    function clearData(address user) external {
        require(msg.sender == user, "Only data owner can delete data.");
        delete datas[user];
    }

    function generateMessage() external {
        require(datas[msg.sender].length > 0, "No data stored");
        string memory message = "";
        for (uint256 i = 0; i < datas[msg.sender].length; i++) {
            message = string(abi.encodePacked(message, datas[msg.sender][i]));
        }
        messages[msg.sender] = message;
        delete datas[msg.sender];
        emit SummarizeData(msg.sender);
    }

    function getMessage(
        address user
    ) external view returns (string memory _summary) {
        return messages[user];
    }

    function clearMessage(address user) external {
        require(msg.sender == user, "Only data owner can delete data summary.");
        _clearMessage();
    }

    function _clearMessage() internal {
        delete messages[msg.sender];
    }

    function emitSignMessage(
        string calldata _message,
        string calldata signature,
        SignMessage decision
    ) external onlyValidator {
        // uint256 initGasLegt = gasleft();
        require(
            messageSigned[msg.sender][_message] == SignMessage.unsigned,
            "Message already signed"
        );
        messageSigned[msg.sender][_message] = decision;
        emit CreateSignature(msg.sender, _message, signature, decision);
        // uint256 endGasLegt = gasleft();
        // _gasUsed = initGasLegt - endGasLegt;
    }

    function signMessage(
        string calldata _message,
        string calldata signature,
        SignMessage decision
    ) external onlyValidator {
        // uint256 initGasLegt = gasleft();
        require(
            messageSigned[msg.sender][_message] == SignMessage.unsigned,
            "Message already signed"
        );
        messageSigned[msg.sender][_message] = decision;
        signatures[msg.sender][_message] = signature;
        // uint256 endGasLegt = gasleft();
        // _gasUsed = initGasLegt - endGasLegt;
    }

    function _isValidMessage(string memory message) internal {
        uint256 _totalSigned = 0;
        for (uint256 i = 0; i < validators.length; i++) {
            address validator = validators[i].walletAddress;

            if (messageSigned[validator][message] == SignMessage.unsigned) {
                _slash(validator, stakeAmount / 10);
                continue;
            }
            if (messageSigned[validator][message] == SignMessage.signed) {
                _totalSigned++;
            }
        }
        if (_totalSigned >= totalValidators / 2) {
            revert SignatureNotEnough(_totalSigned, totalValidators);
        }
    }

    function sendMessageCCIP(
        string calldata _message,
        uint64 destinationChainSelector,
        address receiver
    )
        external
        returns (
            // ZKProof calldata proof
            bytes32 messageId
        )
    {
        // _isValidMessage(_message);
        Client.EVM2AnyMessage memory message = Client.EVM2AnyMessage({
            receiver: abi.encode(receiver),
            data: abi.encode(_message),
            tokenAmounts: new Client.EVMTokenAmount[](0),
            extraArgs: Client._argsToBytes(
                // Additional arguments, setting gas limit and non-strict sequencing mode
                Client.EVMExtraArgsV1({gasLimit: 200_000, strict: false})
            ),
            feeToken: address(0)
        });

        uint256 fees = IRouterClient(i_router).getFee(
            destinationChainSelector,
            message
        );

        if (fees > address(this).balance)
            revert NotEnoughBalance(address(this).balance, fees);

        messageId = IRouterClient(i_router).ccipSend{value: fees}(
            destinationChainSelector,
            message
        );

        emit MessageSent(messageId);
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
