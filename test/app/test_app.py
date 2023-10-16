from fastapi.testclient import TestClient
from web3 import Account
from app.main import app, w3, contract
from app.config import API_KEY

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
