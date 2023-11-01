import { ethers } from "hardhat";
import { Contract, Wallet, providers } from "ethers";
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
import { CCSender__factory } from "../typechain-types";

const proof = {
  scheme: "g16",
  curve: "bn128",
  proof: {
    a: [
      "0x03358f2d2f9cff43953afc741303f6ee69e02a98b55e39b26570b89a5b189311",
      "0x22a750dbd580cc837c54c0280bc16cda73e1ace4a3e607430edb2d2b85b0f1a7",
    ],
    b: [
      [
        "0x066f64bfb362cb12b24ee2ba3102f533b3051437c92531c903d993a03a906edb",
        "0x113fb674e37b1966d03bacd721814b2820abc19aa6cf88c71afdd04361394eeb",
      ],
      [
        "0x2882a4017bcbfeccdbcd9fadda07a176d327afc3a2c6ab021478011fcda5d068",
        "0x2d89f23b64477ac5f638316d6a83f35e04c15dada5103b79209f579e5af8e13e",
      ],
    ],
    c: [
      "0x141f3a676d9bca18ffe86df38c00d8d2248afed29e264a2cdf1ecb34e26beea4",
      "0x23f207b2f3341f195f83724e41398561b464faee394ad1f8ec40afa82daa1a4e",
    ],
  },
  inputs: [
    "0x2243cfe9d7186e0fc9d007a0f8b4ec409a38ad38c9420c7a93ef27d50c342855",
    "0x1275614c43c8302c02b34b86d62f6a3086a89a42e02eb678d3a694d44753fbca",
    "0x000000000000000000000000000000000000000000000000000000000000035f",
    "0x0000000000000000000000000000000000000000000000000000000000000001",
  ],
};

async function main() {
  const wallet = new Wallet(process.env.PRIVATE_KEY || "");
  const provider = new providers.JsonRpcProvider(process.env.SEPOLIA_RPC_URL);
  const signer = wallet.connect(provider);
  const contract = CCSender__factory.connect(
    process.env.SENDER_ADDERSS || "",
    signer
  );

  const message = await contract.getMessage(wallet.address);
  const tx = await contract.sendMessagePayNative(
    BigInt(process.env.DESTINATION_CHAIN_SELECTOR || ""), //sepolia
    process.env.RECEIVER_ADDRESS || "",
    message,
    {
      gasLimit: 1000000,
    }
  );
  const receipt = await tx.wait();
  console.log(receipt);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
