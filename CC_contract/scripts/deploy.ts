import { ethers } from "hardhat";
import { Contract } from "ethers";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";

async function main() {
  let cc: Contract;
  let owner: SignerWithAddress;

  [owner] = await ethers.getSigners();
  const CompactCertificateSender = await ethers.getContractFactory(
    "CompactCertificateSender"
  );

  console.log("Deploying CompactCertificateSender...");
  cc = await CompactCertificateSender.deploy();
  await cc.deployed();
  console.log(`CompactCertificateSender Deployed to -> ${cc.address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
