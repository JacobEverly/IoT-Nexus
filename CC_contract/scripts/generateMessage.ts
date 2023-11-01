import { ethers } from "hardhat";
import { Contract, Wallet, providers } from "ethers";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { CCSender__factory } from "../typechain-types";

async function main() {
  const wallet = new Wallet(process.env.PRIVATE_KEY || "");
  const provider = new providers.JsonRpcProvider(process.env.SEPOLIA_RPC_URL);
  const signer = wallet.connect(provider);
  const contract = CCSender__factory.connect(
    process.env.SENDER_ADDERSS || "",
    signer
  );

  const pk = "0b822b57bc26443586c46ffd9990674fd42ad84a31fec9e049cf3e35b6391bc3";
  const tx = await contract.storeData("Hello");
  await tx.wait();

  const tx2 = await contract.storeData("World");
  await tx2.wait();

  const tx4 = await contract.storeData("2");
  await tx4.wait();

  const tx3 = await contract.generateMessage();
  await tx3.wait();

  const message = await contract.getMessage(wallet.address);
  console.log(message);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
