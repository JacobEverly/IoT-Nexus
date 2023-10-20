
from web3._utils.events import get_event_data
from py_cc.eddsa import Eddsa, Signature
from py_cc.certificate import Attestor


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
