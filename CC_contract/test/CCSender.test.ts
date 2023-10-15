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

  describe("Data Testing", async function () {
    it("Store the data", async function () {
      await compactCertificateSender.storeData("Hello");
      const data = await compactCertificateSender.getData(owner.address);
      expect(data[0]).to.equal("Hello");
    });

    it("Store multiple data", async function () {
      await compactCertificateSender.storeData("World");
      const data = await compactCertificateSender.getData(owner.address);
      expect(data[0]).to.equal("Hello");
      expect(data[1]).to.equal("World");
    });

    it("Delete the data", async function () {
      await compactCertificateSender.storeData("Hello");
      await compactCertificateSender.clearData(owner.address);
      const data = await compactCertificateSender.getData(owner.address);
      expect(data.length).to.equal(0);
    });

    describe("Signature Testing", async function () {
      it("summarize", async function () {
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

      it("summarize multiple data", async function () {
        await compactCertificateSender.storeData("World");
        await compactCertificateSender.summarizeData();
        const messageHash = await compactCertificateSender.getSummarizedMessage(
          owner.address
        );
        const abiEncoded = utils.defaultAbiCoder.encode(
          ["string[]"],
          [["Hello", "World"]]
        );
        const abiEncodedHash = utils.keccak256(abiEncoded);
        expect(messageHash).to.equal(abiEncodedHash);
      });

      it("Delete the data", async function () {
        await compactCertificateSender.clearDataSummary(owner.address);
        const data = await compactCertificateSender.getSummarizedMessage(
          owner.address
        );

        expect(data).to.equal(
          "0x0000000000000000000000000000000000000000000000000000000000000000"
        );
      });
    });
  });
});
