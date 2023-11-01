import { ethers } from "hardhat";
import { Contract, Wallet, providers } from "ethers";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { CompactCertificateSender__factory } from "../typechain-types";

// Mumbai: 0x7956f173922C83579AC6C82abBB7feb810C3Aeea
async function main() {
  const wallet = new Wallet(process.env.PRIVATE_KEY || "");
  const provider = new providers.JsonRpcProvider(process.env.MUMBAI_RPC_URL);
  const signer = wallet.connect(provider);
  const contract = CompactCertificateSender__factory.connect(
    process.env.SENDER_ADDERSS || "",
    signer
  );

  const pk = "0b822b57bc26443586c46ffd9990674fd42ad84a31fec9e049cf3e35b6391bc3";
  const tx = await contract.setValidator(wallet.address, pk, {
    // value: ethers.utils.parseEther("0.00001"),
    value: 10000,
    gasLimit: 1000000,
  });
  const receipt = await tx.wait();

  const validator = await contract.getValidator(wallet.address);
  console.log(validator);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
