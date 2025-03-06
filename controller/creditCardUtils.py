import requests

from model.requestError import RequestError

DISTANT_PAYMENT_URL = "https://dimensweb.uqac.ca/~jgnault/shops/pay/"


def check_credit_card_entity_complete(credit_card_info):
    required_fields = ["name", "number", "expiration_year", "cvv", "expiration_month"]
    if not all(credit_card_info.get(field) for field in required_fields):
        raise RequestError("missing-fields", 422, "La mise à jour d'une commande nécessite une carte de crédit")
    return True

def send_card_data_distant_payment(card_data, amount):
    payload = {
        "credit_card": card_data,
        "amount_charged": amount
    }
    headers = {
        "Content-Type": "application/json"
    }
    res = requests.post(DISTANT_PAYMENT_URL, json=payload, headers=headers)

    # Si la requête a échoué, on retourne l'erreur
    if res.status_code != 200:
        raise RequestError(res.json()["errors"]["credit_card"]["code"], res.status_code,
                           res.json()["errors"]["credit_card"]["name"])

    return res.json()
