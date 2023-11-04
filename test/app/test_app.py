from fastapi.testclient import TestClient
from web3 import Account
from app.main import app, w3, contract
from app.config import API_KEY
from app.db import attenstors


client = TestClient(app)
account = Account.from_key(API_KEY)


def call_function(function, *arg, gas_limit=200000, value=0):
    nonce = w3.eth.get_transaction_count(account.address)
    txn = function(*arg).build_transaction({
        'from': account.address,
        'gas': gas_limit,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
        'value': value
    })
    signed_txn = Account.sign_transaction(txn, API_KEY)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    print(txn_receipt)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Event listener is running!"}


def test_listen_event():
    # call_function(contract.functions.storeData, "9487")
    call_function(contract.functions.summarizeData)
    print("ok")


def test_upload():
    response = client.post(
        "/upload", json={"inputCount": 2, "inputMessage": "9487"})
    assert response.status_code == 200

    data = response.json()
    assert data.get("data1") is not None
    assert data.get("data2") is not None
    assert data.get("data3") is not None
    assert data.get("genCertTime") is not None
    assert data.get("compileZokTime") is not None
    assert data.get("computeTime") is not None
    assert data.get("verifyTime") is not None


def test_sign():
    response = client.post(
        "/sign",
        json={
            "message": "9487",
            "attestor": list(attenstors.keys())[0]
        }
    )
    assert response.status_code == 200
