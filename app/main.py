import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import subprocess
from app.utils import handle_event, sign_message
from app.db import get_attestor, save_signed_message

app = FastAPI()
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


@app.post("/upload")
async def upload(request: Request):
    input_data = await request.json()
    input_count = input_data["inputCount"]
    input_message = input_data["inputMessage"]
    print(input_count, input_message)

    run_command = (
        "python3 main.py -n "
        + str(input_count)
        + " -m "
        + str(input_message)
    )
    print(run_command)
    result = subprocess.run(run_command, shell=True, capture_output=True)
    print(result)
    genCertTime = result.stdout.decode("utf-8").strip().split(" ")[-1]

    # generate zkproof
    run_command_zoc = "cd zokratesjs && node index.js && cd .."

    zoc_result = subprocess.run(
        run_command_zoc,
        shell=True,
        capture_output=True).stdout.decode('utf-8')
    compileZokTime, computeTime, verifyTime, _ = [s.strip().split(
        " ")[-1] for s in zoc_result.split('\n')]

    print(compileZokTime, computeTime, verifyTime)

    with open("certificate.json") as f:
        data1 = json.load(f)

    with open("./zokratesjs/proof.json") as f:
        data2 = json.load(f)

    with open("attest.txt") as f:
        lines = f.read().splitlines()
        data3 = []
        for count, line in enumerate(lines):
            if count < int(input_count):
                public_key, weight = line.split(",")
                data3.append({"public_key": public_key, "weight": weight})
    data = {
        "data1": data1,
        "data2": data2,
        "data3": data3,
        "genCertTime": genCertTime + " sec",
        "compileZokTime": f"Compile Zokrates: {compileZokTime} sec",
        "computeTime": f"Compute Witness & Generate Proof: {computeTime} sec",
        "verifyTime": f"Verify Proof: {verifyTime} sec"
    }

    return JSONResponse(content=data)


@app.post("/sign")
async def sign(request: Request):
    input_data = await request.json()
    message = input_data["message"]
    attestor_s = input_data["attestor"]
    print(message, attestor_s)

    attestor = get_attestor(attestor_s)
    signature = sign_message(message, attestor)
    save_signed_message(message, signature)
    return True


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(listen_to_events())
