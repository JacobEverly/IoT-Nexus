from fastapi.testclient import TestClient
from app import utils
from app.main import app
from app.db import validators, messages
from app.models import Message


client = TestClient(app)
validator = validators[list(validators.keys())[0]]
message = messages[list(messages.keys())[0]]


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Event listener is running!"}


def test_listen_event():
    w3 = utils.get_w3()
    contract = utils.get_contract(w3=w3)
    # utils.call_function(contract.functions.storeData, message.message, w3=w3)
    # utils.call_function(contract.functions.summarizeData, w3=w3)
    print("ok")


# def test_upload():
#     response = client.post(
#         "/upload", json={"inputCount": 2, "inputMessage": "9487"})
#     assert response.status_code == 200

#     data = response.json()
#     assert data.get("data1") is not None
#     assert data.get("data2") is not None
#     assert data.get("data3") is not None
#     assert data.get("genCertTime") is not None
#     assert data.get("compileZokTime") is not None
#     assert data.get("computeTime") is not None
#     assert data.get("verifyTime") is not None


def test_signMessage():
    response = client.post(
        "/api/signMessage",
        json={
            "message": message.message,
            "wallet_address": validator.wallet_address
        }
    )
    assert response.status_code == 200


def test_getKey():
    response = client.post(
        "/api/getKey",
        json={
            "wallet_address": validator.wallet_address
        }
    )
    assert response.status_code == 200
    assert response.json().get("public_key") is not None
    assert response.json().get("private_key") is not None


def test_signUp():
    response = client.post(
        "/api/signUp",
        data={
            "wallet_address": validator.wallet_address,
            "weight": validator.weight
        }
    )
    assert response.status_code == 200

    response = client.post(
        "/api/signUp",
        data={
            "wallet_address": "0x0000000",
            "weight": validator.weight
        }
    )
    assert response.status_code == 404


def test_signIn():
    response = client.post(
        "/api/signIn",
        data={
            "wallet_address": validator.wallet_address
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    assert response.status_code == 200

    response = client.post(
        "/api/signIn",
        data={
            "wallet_address": "0x0000000"
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    assert response.status_code == 404


def test_genProof():
    response = client.post(
        "/api/genProof",
        json={
            "count": 2,
            "message": message.message
        }
    )
    assert response.status_code == 200
    assert response.json().get("proof") is not None


def test_getMessages():
    response = client.get("/db/messages")
    assert response.status_code == 200

    messages = response.json()
    assert len(messages) > 0
    for key in Message.model_fields.keys():
        assert key in messages[0]
    assert "private_key" not in messages[0].get("signed_validators")[0]
