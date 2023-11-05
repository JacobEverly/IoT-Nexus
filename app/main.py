import asyncio
import json
import subprocess
from typing import Annotated, List
from fastapi import FastAPI, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware


from app import db
from app import utils
from app.models import (
    SignMessageRequest, GenProofRequest, GenKeyRequest, PKeys, Message)

origins = [
    "http://localhost:5173",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def read_root():
    return {"message": "Event listener is running!"}


async def listen_to_events():
    w3 = utils.get_w3()
    contract_address = utils.get_contract_address()
    abi = utils.get_abi()
    contract = utils.get_contract(w3, contract_address, abi)
    event_template = contract.events.GenerateMessage

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
            suc, res = utils.handle_event(
                event=event,
                event_template=event_template
            )
            if suc:
                new_event = True
                print("Event found", res)
        # print("No new event" if not new_event else "New event found")
        block_start = block_end + 1
        await asyncio.sleep(3)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(listen_to_events())


@app.post("/api/genProof")
async def genproof(request: GenProofRequest):
    command = (
        "python3 main.py -n "
        + str(request.count)
        + " -m "
        + str(request.message)
    )
    result = subprocess.run(command, shell=True, capture_output=True)
    genCertTime = result.stdout.decode("utf-8").strip().split(" ")[-1]

    # generate zkproof
    command_zoc = "cd zokratesjs && node index.js && cd .."
    zoc_result = subprocess.run(
        command_zoc,
        shell=True,
        capture_output=True).stdout.decode('utf-8')
    compileZokTime, computeTime, verifyTime, _ = [s.strip().split(
        " ")[-1] for s in zoc_result.split('\n')]

    # with open("certificate.json") as f:
    #     certificate = json.load(f)

    with open("./zokratesjs/proof.json") as f:
        proof = json.load(f)

    # with open("attest.txt") as f:
    #     lines = f.read().splitlines()
    #     validators = []
    #     for count, line in enumerate(lines):
    #         if count < int(request.count):
    #             public_key, weight = line.split(",")
    #             validators.append({"public_key": public_key, "weight": weight})

    # data = GenProofResponse(**{
    #     "certificate": certificate,
    #     "proof": proof,
    #     "validators": validators,
    #     "genCertTime": genCertTime + " sec",
    #     "compileZokTime": compileZokTime,
    #     "computeTime": computeTime,
    #     "verifyTime": verifyTime
    # })

    return JSONResponse(content=proof)


@app.post("/api/signMessage")
async def sign_message(request: SignMessageRequest):
    attestor = db.get_attestor(request.wallet_address)

    message = request.message
    signature = utils.sign_message(message, attestor)
    db.save_signature(message, signature)
    return Response(status_code=200)


@app.post("/api/getKey")
async def get_key(request: GenKeyRequest):
    sk = utils.gen_sk()
    db.save_tmp_key_map(request.wallet_address, sk)
    keys = PKeys(
        public_key=sk.get_public_key().toString(),
        private_key=sk.toString()
    )
    return JSONResponse(
        content=jsonable_encoder(keys)
    )


@app.post("/api/signUp")
async def signup(
    wallet_address: Annotated[str, Form()],
    weight: Annotated[int, Form()]
):
    if wallet_address not in db.validators:
        return Response(status_code=404)
    sk = db.get_tmp_key_map(wallet_address)

    db.save_validator_and_attestor(
        sk=sk,
        weight=weight,
        wallet_address=wallet_address
    )
    return Response(status_code=200)


@app.post("/api/signIn")
async def signin(wallet_address: Annotated[str, Form()]):
    if wallet_address in db.validators:
        return Response(status_code=200)
    return Response(status_code=404)


@app.get("/db/messages")
async def get_messages() -> List[dict]:
    messages = list(db.messages.values())
    return_messages = []
    for message in messages:
        return_messages.append({
            "message": message.message,
            "signed_validators": [
                utils.export_validator(v) for v in message.signed_validators
            ],
            "created_at": message.created_at
        })
    return return_messages

# @app.post("/upload")
# async def upload(request: Request):
#     input_data = await request.json()
#     input_count = input_data["inputCount"]
#     input_message = input_data["inputMessage"]
#     print(input_count, input_message)

#     run_command = (
#         "python3 main.py -n "
#         + str(input_count)
#         + " -m "
#         + str(input_message)
#     )
#     print(run_command)
#     result = subprocess.run(run_command, shell=True, capture_output=True)
#     print(result)
#     genCertTime = result.stdout.decode("utf-8").strip().split(" ")[-1]

#     # generate zkproof
#     run_command_zoc = "cd zokratesjs && node index.js && cd .."

#     zoc_result = subprocess.run(
#         run_command_zoc,
#         shell=True,
#         capture_output=True).stdout.decode('utf-8')
#     compileZokTime, computeTime, verifyTime, _ = [s.strip().split(
#         " ")[-1] for s in zoc_result.split('\n')]

#     print(compileZokTime, computeTime, verifyTime)

#     with open("certificate.json") as f:
#         data1 = json.load(f)

#     with open("./zokratesjs/proof.json") as f:
#         data2 = json.load(f)

#     with open("attest.txt") as f:
#         lines = f.read().splitlines()
#         data3 = []
#         for count, line in enumerate(lines):
#             if count < int(input_count):
#                 public_key, weight = line.split(",")
#                 data3.append({"public_key": public_key, "weight": weight})
#     data = {
#         "data1": data1,
#         "data2": data2,
#         "data3": data3,
#         "genCertTime": genCertTime + " sec",
#         "compileZokTime": f"Compile Zokrates: {compileZokTime} sec",
#         "computeTime": f"Compute Witness & Generate Proof: {computeTime} sec",
#         "verifyTime": f"Verify Proof: {verifyTime} sec"
#     }

#     return JSONResponse(content=data)
