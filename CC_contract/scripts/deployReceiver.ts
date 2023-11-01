import { ethers } from "hardhat";
import { Contract } from "ethers";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";

// Sepolia: 0x5d5aB6CA654835C0Cf11f230EB3Bfb44f6ffdF7B
async function main() {
  let cc: Contract;
  let owner: SignerWithAddress;

  [owner] = await ethers.getSigners();
  const CompactCertificateReceiver = await ethers.getContractFactory(
    "CCReceiver"
  );

  console.log("Deploying CompactCertificateReceiver...");
  const router = process.env.RECEIVER_ROUTER || "";
  cc = await CompactCertificateReceiver.deploy(router);
  await cc.deployed();
  console.log(`CompactCertificateSender Deployed to -> ${cc.address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
