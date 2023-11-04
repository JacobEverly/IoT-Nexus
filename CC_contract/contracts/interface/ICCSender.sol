// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.19;

import {SignMessage} from "../types/message.sol";

interface ICCSender {
    function setStakeAmount(uint256 amount) external;

    function setValidator(
        address validator,
        string memory eddsaPublicKey
    ) external payable;

    function removeValidator(address validator) external;

    function withdrawStake() external payable;

    function storeData(string memory data) external;

    function getData(address user) external view returns (string[] memory);

    function clearData(address user) external;

    function GenerateMessage() external;

    function getMessage(
        address user
    ) external view returns (string memory _summary);

    function clearDataSummary(address user) external;

    function signMessage(string memory _message, SignMessage decision) external;

    function sendMessageCCIP(
        string memory message,
        uint256 _nonce,
        bytes[] calldata _multiSignature
    ) external;
}
