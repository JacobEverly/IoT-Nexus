import { useState } from "react";
import { ethers } from "ethers";
import { isValidWalletAddress } from "@/utils/address";

const useEtherWallet = () => {
  const [isConnect, setIsConnect] = useState(false);
  const [address, setAddress] = useState();
  const provider = new ethers.providers.Web3Provider(window.ethereum);
  const signer = provider.getSigner();

  async function connectWallet() {
    if (!window.ethereum) {
      alert("Please install MetaMask browser extension!");
      return;
    }

    const accounts = await window.ethereum.request({
      method: "eth_requestAccounts",
    });
    const defaultAccount = accounts[0];
    if (isValidWalletAddress(defaultAccount)) {
      setIsConnect(true);
      setAddress(defaultAccount);
    }
    return defaultAccount;
  }

  async function switchNetwork(network) {
    try {
      await window.ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: network }],
      });
    } catch (switchError) {
      if (switchError.code === 4902 || switchError.code === -32603) {
        // switchEorror code=> Webpage: 4092, Mobile: -32603
        try {
          await window.ethereum.request({
            method: "wallet_addEthereumChain",
            params: [chainTable.get(network)],
          });
        } catch (addError) {
          console.log(addError);
        }
      }
    }
  }

  return { isConnect, address, provider, signer, connectWallet, switchNetwork };
};

export default useEtherWallet;
