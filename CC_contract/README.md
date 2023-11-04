# Sample Hardhat Project

This project demonstrates a basic Hardhat use case. It comes with a sample contract, a test for that contract, and a script that deploys that contract.

Try running some of the following tasks:

1. CompactCertificateSender.sol

   - deploy: sepolia
   - address: 0xB04bA863cA47DfbA054F11CA0BAE5e84823B95aF

2. CompactCertificateReceiver.sol

- deploy: mumbai
- address: 0xA5eC1B3eB74F10A1aea78fAb961F0E319BFc5353

### Run compile & test & deploy

```shell
npx hardhat compile
npx hardhat test
npx hardhat run --network sepolia scripts/deploySender.ts
npx hardhat run --network sepolia scripts/deployReceiver.ts
```

### Run script

```shell
npx hardhat run --network sepolia scripts/<script>.ts
```
