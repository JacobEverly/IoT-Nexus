import asyncio
from fastapi import FastAPI
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3._utils.events import get_event_data
import json

app = FastAPI()
# with open("CC_contract/contracts/CompactCertificateSender.sol") as f:
#     contract_source_code = f.read()

# compiled_sol = compile_source(contract_source_code)
# contract_interface = compiled_sol['<stdin>:CompactCertificateSender']
with open("CC_contract/contracts/CompactCertificateSender.json") as f:
    abi = json.load(f)["result"]
contract_address = "0xcb2ba48E38EfDAF43F1C62e72a88e4754D68d23d"
w3 = Web3(Web3.HTTPProvider(
    'https://polygon-mumbai.infura.io/v3/23a668257ecb4ece82ff765e85972ef7'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(
    address=contract_address, abi=abi
)
event_template = contract.events.SummarizeData


def handle_event(event, event_template):
    try:
        result = get_event_data(
            event_template.w3.codec,
            event_template._get_event_abi(),
            event
        )
        return True, result
    except:
        return False, None


@app.get('/')
async def read_root():
    return {"message": "Event listener is running!"}


async def listen_to_events():
    block_start = w3.eth.get_block_number()
    while True:
        block_end = w3.eth.get_block_number()
        events = w3.eth.get_logs({
            'fromBlock': block_start,
            'toBlock': block_end,
            'address': contract_address
        })
        new_event = False
        for event in events:
            suc, res = handle_event(
                event=event,
                event_template=event_template
            )
            if suc:
                new_event = True
                print("Event found", res)
        print("No new event" if not new_event else "New event found")
        block_start = block_end + 1
        await asyncio.sleep(3)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(listen_to_events())
