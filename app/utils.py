
import json
from dotenv.main import dotenv_values
from web3._utils.events import get_event_data
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3 import Account

from app.config import API_KEY
from app.models import Validator
from py_cc.certificate import Attestor
from py_cc.elliptic_curves.baby_jubjub import curve
from py_cc.eddsa import Eddsa, Signature
from py_cc.keys import PrivateKey


def gen_sk() -> PrivateKey:
    return PrivateKey(curve=curve)


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


def sign_message(message: str, attestor: Attestor) -> Signature:
    return Eddsa.sign(message, attestor.getPrivateKey(), attestor.public_key)


def get_contract_address():
    config = dotenv_values("CC_contract/.env")
    address = config["SENDER_ADDERSS"]
    return address


def get_abi():
    with open("CC_contract/contracts/CompactCertificateSender.json") as f:
        abi = json.load(f)
    return abi


def get_w3():
    w3 = Web3(Web3.HTTPProvider(
        'https://polygon-mumbai.infura.io/v3/23a668257ecb4ece82ff765e85972ef7'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


def get_contract(w3=get_w3(), contract_address=get_contract_address(), abi=get_abi()):
    return w3.eth.contract(address=contract_address, abi=abi)


def call_function(function, *arg, gas_limit=200000, value=0, w3=get_w3()):
    account = Account.from_key(API_KEY)
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


def export_validator(validator: Validator):
    return {
        "public_key": validator.public_key,
        "weight": validator.weight,
        "wallet_address": validator.wallet_address
    }
