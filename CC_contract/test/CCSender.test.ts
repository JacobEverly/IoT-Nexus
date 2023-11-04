import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { ethers } from "hardhat";
import { Contract, utils } from "ethers";
import { expect } from "chai";
import { CCSender } from "../typechain-types";

describe("CompactCertificateSender", function () {
  let CCSender: Contract;
  let compactCertificateSender: CCSender;
  let owner: SignerWithAddress;
  let addr1: SignerWithAddress;

  const setupAddresses = async () => {
    [owner, addr1] = await ethers.getSigners();
  };

  const deployContract = async () => {
    // Deploy the Linkt contract
    const CCSenderFactory = await ethers.getContractFactory("CCSender");
    compactCertificateSender = await CCSenderFactory.deploy(
      "0x70499c328e1E2a3c41108bd3730F6670a44595D1",
      10000
    );
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
  });

  describe("Message Testing", async function () {
    it("summarize", async function () {
      await compactCertificateSender.storeData("Hello");
      await compactCertificateSender.generateMessage();
      const messageHash = await compactCertificateSender.getMessage(
        owner.address
      );
      // const abiEncoded = utils.defaultAbiCoder.encode(
      //   ["string[]"],
      //   [["Hello"]]
      // );
      // const abiEncodedHash = utils.keccak256(abiEncoded);
      expect(messageHash).to.equal("Hello");
    });

    it("summarize multiple data", async function () {
      await compactCertificateSender.storeData("World");
      await compactCertificateSender.generateMessage();
      const messageHash = await compactCertificateSender.getMessage(
        owner.address
      );
      // const abiEncoded = utils.defaultAbiCoder
      //   .encode(["string[]"], [["Hello", "World"]])
      //   .toString();
      // const abiEncodedHash = utils.keccak256(abiEncoded);
      expect(messageHash).to.equal("HelloWorld");
    });

    it("Delete the data", async function () {
      await compactCertificateSender.clearMessage(owner.address);
      const data = await compactCertificateSender.getMessage(owner.address);

      expect(data).to.equal("");
    });
  });

  describe("Validator Testing", async function () {
    it("set validator", async function () {
      const pk =
        "0b822b57bc26443586c46ffd9990674fd42ad84a31fec9e049cf3e35b6391bc3";

      const stakeAmount = await compactCertificateSender.stakeAmount();
      await compactCertificateSender.setValidator(owner.address, pk, {
        value: stakeAmount,
      });

      const validator = await compactCertificateSender.getValidator(
        owner.address
      );
      expect(validator.walletAddress).to.equal(owner.address);
    });

    it("remove validator", async function () {
      const balance = await owner.getBalance();
      await compactCertificateSender.removeValidator(owner.address);
      const validator = await compactCertificateSender.getValidator(
        owner.address
      );
      expect(validator.isValid).to.equal(false);
    });
  });

  describe("Signature Testing", async function () {
    const message = "Hello";
    const pk1 =
      "0b822b57bc26443586c46ffd9990674fd42ad84a31fec9e049cf3e35b6391bc3";

    const signature1 = "0b822asdf6ffd9990674fd42ad84a31fec9e049cf3e35b6391bc3";
    const pk2 =
      "0b822b57bc26443586c46ffd9990674fd42ad84a31fec9e049cf3e35b6391bc2";

    const signature2 =
      "0b822asdf6ffd9990674fd42ad84a31fec9asdfe049cf3e35b6391bc3";
    it("sign message", async function () {
      await compactCertificateSender.storeData(message);
      await compactCertificateSender.generateMessage();
      const messageHash = await compactCertificateSender.getMessage(
        owner.address
      );

      const stakeAmount = await compactCertificateSender.stakeAmount();
      await compactCertificateSender.setValidator(owner.address, pk1, {
        value: stakeAmount,
      });

      const tx = await compactCertificateSender.signMessage(
        messageHash,
        signature1,
        2
      );
      const receipt = await tx.wait();
      console.log(receipt);

      const decision = await compactCertificateSender.messageSigned(
        owner.address,
        messageHash
      );
      expect(decision).to.equal(2);
    });

    it("emit sign message", async function () {
      const stakeAmount = await compactCertificateSender.stakeAmount();
      await compactCertificateSender.setValidator(addr1.address, pk2, {
        value: stakeAmount,
      });
      const messageHash = await compactCertificateSender.getMessage(
        owner.address
      );

      const tx = await compactCertificateSender
        .connect(addr1)
        .signMessage(messageHash, signature2, 2);
      const receipt = await tx.wait();
      console.log(receipt);

      const decision = await compactCertificateSender.messageSigned(
        addr1.address,
        messageHash
      );
      expect(decision).to.equal(2);
    });

    it("send message", async function () {
      const message = await compactCertificateSender.getMessage(owner.address);

      const proof = {
        scheme: "ecdsa",
        curve: "jobjob",
        proof: {
          a: ["123"],
          b: [["123", "456"]],
          c: ["123"],
        },
        inputs: ["123"],
      };
      const tx = await compactCertificateSender.sendMessageCCIP(
        BigInt("16015286601757825753"), //sepolia
        "0x9f88C837dF98a16c7B05aCb527c18742ac47455C",
        message,
        proof
      );
      const receipt = await tx.wait();
      console.log(receipt);
    });
  });
});
