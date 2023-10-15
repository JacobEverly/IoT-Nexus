import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { ethers } from "hardhat";
import { Contract, utils } from "ethers";
import { expect } from "chai";
import { CompactCertificateSender } from "../typechain-types";

describe("CompactCertificateSender", function () {
  let CCSender: Contract;
  let compactCertificateSender: CompactCertificateSender;
  let owner: SignerWithAddress;
  let otherAccount: SignerWithAddress;

  const setupAddresses = async () => {
    [owner, otherAccount] = await ethers.getSigners();
  };

  const deployContract = async () => {
    // Deploy the Linkt contract
    const CCSenderFactory = await ethers.getContractFactory(
      "CompactCertificateSender"
    );
    compactCertificateSender = await CCSenderFactory.deploy();
    await compactCertificateSender.deployed();
  };
  before(async () => {
    await setupAddresses();
    await deployContract();
  });

  describe("Publishing Data", async function () {
    it("Store the data", async function () {
      await compactCertificateSender.storeData("Hello");
      const data = await compactCertificateSender.getData(owner.address);
      expect(data[0]).to.equal("Hello");
    });
  });

  describe("Summarize Data", async function () {
    it("Store the data", async function () {
      await compactCertificateSender.storeData("Hello");
      await compactCertificateSender.summarizeData();
      const messageHash = await compactCertificateSender.getSummarizedMessage(
        owner.address
      );
      const abiEncoded = utils.defaultAbiCoder.encode(
        ["string[]"],
        [["Hello"]]
      );
      const abiEncodedHash = utils.keccak256(abiEncoded);
      expect(messageHash).to.equal(abiEncodedHash);
    });
  });
});
