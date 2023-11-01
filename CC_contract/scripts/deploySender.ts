import { ethers } from "hardhat";
import { Contract } from "ethers";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";

// Mumbai: 0xfc815FA7d416a6eBFF0E60A103d4c061DEB2f27F
async function main() {
  let cc: Contract;
  let owner: SignerWithAddress;

  [owner] = await ethers.getSigners();
  const CompactCertificateSender = await ethers.getContractFactory(
    "CompactCertificateSender"
  );

  console.log("Deploying CompactCertificateSender...");
  const router = "0x70499c328e1E2a3c41108bd3730F6670a44595D1";
  cc = await CompactCertificateSender.deploy(router, 10000);
  await cc.deployed();
  console.log(`CompactCertificateSender Deployed to -> ${cc.address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
