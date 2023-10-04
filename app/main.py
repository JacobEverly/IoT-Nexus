from fastapi import FastAPI
from web3 import Web3
from solcx import compile_source
import asyncio

app = FastAPI()
with open("app/lost_ether.sol") as f:
    contract_source_code = f.read()

compiled_sol = compile_source(contract_source_code)
contract_interface = compiled_sol['<stdin>:TestToken']
contract_address = "0x2cBB2d8787EaA3A9aE71eE71ef232e828108395c"


@app.get('/')
async def read_root():
    return {"message": "Event listener is running!"}


async def listen_to_events():
    w3 = Web3(Web3.HTTPProvider(
        'https://sepolia.infura.io/v3/23a668257ecb4ece82ff765e85972ef7'))
    contract = w3.eth.contract(
        address=contract_address, abi=contract_interface['abi'])
    block = w3.eth.get_block('latest')
    event_filter = contract.events.Transfer.create_filter(
        fromBlock=block.number)

    while True:
        print("new:", event_filter.get_new_entries())
        print("all:", event_filter.get_all_entries())
        # for event in event_filter.get_all_entries():
        #     print(event)
        await asyncio.sleep(3)

# Start the event listener when the app starts


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(listen_to_events())
