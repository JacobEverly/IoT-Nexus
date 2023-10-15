# Sample Hardhat Project

This project demonstrates a basic Hardhat use case. It comes with a sample contract, a test for that contract, and a script that deploys that contract.

Try running some of the following tasks:

1. CompactCertificateSender.sol
   - deploy: mumbai
   - address: 0xcb2ba48E38EfDAF43F1C62e72a88e4754D68d23d
   - function:
     - storeData(string memory \_data)
     - getData()
     - clearData(address \_address)
     - summarizeData(address \_address)
     - getSummarizedMessage()
     - clearDataSummary(address \_address) # should change the function name

```shell
npx hardhat help
npx hardhat test
REPORT_GAS=true npx hardhat test
npx hardhat node
npx hardhat run scripts/deploy.ts
```
