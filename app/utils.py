
from web3._utils.events import get_event_data


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
