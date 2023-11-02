// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import {IRouterClient} from "@chainlink/contracts-ccip/src/v0.8/ccip/interfaces/IRouterClient.sol";
import {OwnerIsCreator} from "@chainlink/contracts-ccip/src/v0.8/shared/access/OwnerIsCreator.sol";
import {Client} from "@chainlink/contracts-ccip/src/v0.8/ccip/libraries/Client.sol";
import {CCIPReceiver} from "@chainlink/contracts-ccip/src/v0.8/ccip/applications/CCIPReceiver.sol";
import {IERC20} from "@chainlink/contracts-ccip/src/v0.8/vendor/openzeppelin-solidity/v4.8.0/token/ERC20/IERC20.sol";
import {ZKProof} from "./types/proof.sol";

/**
 * THIS IS AN EXAMPLE CONTRACT THAT USES HARDCODED VALUES FOR CLARITY.
 * THIS IS AN EXAMPLE CONTRACT THAT USES UN-AUDITED CODE.
 * DO NOT USE THIS CODE IN PRODUCTION.
 */

/// @title - A simple messenger contract for sending/receving string data across chains.
contract CCSender is CCIPReceiver {
    enum SignMessage {
        unsigned,
        rejected,
        signed
    }

    // Custom errors to provide more descriptive revert messages.
    error SignatureNotEnough(uint signatures, uint totalValidators);
    error NotEnoughBalance(uint256 currentBalance, uint256 calculatedFees); // Used to make sure contract has enough balance.
    error NothingToWithdraw(); // Used when trying to withdraw Ether but there's nothing to withdraw.
    error FailedToWithdrawEth(address owner, address target, uint256 value); // Used when the withdrawal of Ether fails.
    error DestinationChainNotAllowlisted(uint64 destinationChainSelector); // Used when the destination chain has not been allowlisted by the contract owner.
    error SourceChainNotAllowlisted(uint64 sourceChainSelector); // Used when the source chain has not been allowlisted by the contract owner.
    error SenderNotAllowlisted(address sender); // Used when the sender has not been allowlisted by the contract owner.

    // Event emitted when a message is sent to another chain.
    event MessageSent(
        bytes32 indexed messageId, // The unique ID of the CCIP message.
        uint64 indexed destinationChainSelector, // The chain selector of the destination chain.
        address receiver, // The address of the receiver on the destination chain.
        string text, // The text being sent.
        address feeToken, // the token address used to pay CCIP fees.
        uint256 fees // The fees paid for sending the CCIP message.
    );

    event MessageReceived(
        bytes32 indexed messageId, // The unique ID of the CCIP message.
        uint64 indexed sourceChainSelector, // The chain selector of the source chain.
        address sender, // The address of the sender from the source chain.
        string text // The text that was received.
    );

    struct Validator {
        address walletAddress;
        string eddsaPublicKey;
        bool isValid;
    }

    address public owner;
    uint256 public totalValidators;
    uint256 public totalStakes;
    uint public stakeAmount;
    Validator[] public validators;

    mapping(address => string[]) public datas;
    mapping(address => string) internal messages;
    mapping(address => uint256) private validatorIndex;
    mapping(address => mapping(string => SignMessage)) public messageSigned;
    // mapping(address => mapping(string => string)) public signatures;
    mapping(string => uint256) public messageWeight;
    mapping(address => uint256) public stakes;
    uint256 public nonce;

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

    /// @notice Constructor initializes the contract with the router address.
    /// @param _router The address of the router contract.
    /// @param _amount The minimum amount to stake.
    constructor(address _router, uint256 _amount) CCIPReceiver(_router) {
        owner = msg.sender;
        stakeAmount = _amount;
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

    function signMessage(
        string calldata _message,
        string calldata signature,
        SignMessage decision
    ) external onlyValidator {
        require(
            messageSigned[msg.sender][_message] == SignMessage.unsigned,
            "Message already signed"
        );
        messageSigned[msg.sender][_message] = decision;
        if (decision == SignMessage.signed) {
            messageWeight[_message] += 1;
        }
        emit CreateSignature(msg.sender, _message, signature, decision);
    }

    // function signMessage(
    //     string calldata _message,
    //     string calldata signature,
    //     SignMessage decision
    // ) external onlyValidator {
    //     // uint256 initGasLegt = gasleft();
    //     require(
    //         messageSigned[msg.sender][_message] == SignMessage.unsigned,
    //         "Message already signed"
    //     );
    //     messageSigned[msg.sender][_message] = decision;
    //     signatures[msg.sender][_message] = signature;
    //     // uint256 endGasLegt = gasleft();
    //     // _gasUsed = initGasLegt - endGasLegt;
    // }

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

    /// @notice Sends data to receiver on the destination chain.
    /// @notice Pay for fees in native gas.
    /// @dev Assumes your contract has sufficient native gas tokens.
    /// @param _destinationChainSelector The identifier (aka selector) for the destination blockchain.
    /// @param _receiver The address of the recipient on the destination blockchain.
    /// @param _message The text to be sent.
    /// @return messageId The ID of the CCIP message that was sent.
    function sendMessageCCIP(
        uint64 _destinationChainSelector,
        address _receiver,
        string calldata _message
    )
        external
        returns (
            // ZKProof calldata _zkProofs
            bytes32 messageId
        )
    {
        require(
            messageWeight[_message] > totalValidators / 2,
            "proven weight is not enough"
        );
        // Create an EVM2AnyMessage struct in memory with necessary information for sending a cross-chain message
        Client.EVM2AnyMessage memory evm2AnyMessage = Client.EVM2AnyMessage({
            receiver: abi.encode(_receiver), // ABI-encoded receiver address
            data: abi.encode(_message), // ABI-encoded string
            tokenAmounts: new Client.EVMTokenAmount[](0), // Empty array aas no tokens are transferred
            extraArgs: Client._argsToBytes(
                // Additional arguments, setting gas limit and non-strict sequencing mode
                Client.EVMExtraArgsV1({gasLimit: 200_000, strict: false})
            ),
            // Set the feeToken to a feeTokenAddress, indicating specific asset will be used for fees
            feeToken: address(0)
        });
        // Initialize a router client instance to interact with cross-chain router
        IRouterClient router = IRouterClient(this.getRouter());

        // Get the fee required to send the CCIP message
        uint256 fees = router.getFee(_destinationChainSelector, evm2AnyMessage);

        if (fees > address(this).balance)
            revert NotEnoughBalance(address(this).balance, fees);

        // Send the CCIP message through the router and store the returned CCIP message ID
        messageId = router.ccipSend{value: fees}(
            _destinationChainSelector,
            evm2AnyMessage
        );

        // Emit an event with message details
        emit MessageSent(
            messageId,
            _destinationChainSelector,
            _receiver,
            _message,
            address(0),
            fees
        );

        // Return the CCIP message ID
        return messageId;
    }

    /// handle a received message
    function _ccipReceive(
        Client.Any2EVMMessage memory any2EvmMessage
    ) internal override {
        emit MessageReceived(
            any2EvmMessage.messageId,
            any2EvmMessage.sourceChainSelector, // fetch the source chain identifier (aka selector)
            abi.decode(any2EvmMessage.sender, (address)), // abi-decoding of the sender address,
            abi.decode(any2EvmMessage.data, (string))
        );
    }
}
