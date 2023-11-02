import { ethers } from "hardhat";
import { Contract, Wallet, providers } from "ethers";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { CCSender__factory } from "../typechain-types";

// Mumbai: 0x7956f173922C83579AC6C82abBB7feb810C3Aeea
async function main() {
  const wallet = new Wallet(process.env.PRIVATE_KEY || "");
  const provider = new providers.JsonRpcProvider(process.env.SEPOLIA_RPC_URL);
  const signer = wallet.connect(provider);
  const contract = CCSender__factory.connect(
    process.env.SENDER_ADDERSS || "",
    signer
  );

  const message = await contract.getMessage(wallet.address);
  console.log(message);
  const signature1 = "0b822asdf6ffd9990674fd42ad84a31fec9e049cf3e35b6391bc3";
  const tx = await contract.signMessage(message, signature1, 2);
  await tx.wait();
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
