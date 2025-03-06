import pytest
from model.requestError import RequestError
from utils.creditCardUtils import check_credit_card_entity_complete, send_card_data_distant_payment


def test_is_credit_card_entity_complete_success():
    assert check_credit_card_entity_complete({
        "name" : "John Doe",
        "number" : "4000 0000 0000 0002",
        "expiration_year" : 2025,
        "cvv" : "123",
        "expiration_month" : 9
    }) == True

def test_is_credit_card_entity_complete_failure():
    with pytest.raises(RequestError) as e:
        check_credit_card_entity_complete({
            "name": "John Doe",
            # "number": "4000 0000 0000 0002",
            "expiration_year": 2025,
            "cvv": "123",
            "expiration_month": 9
        })
    assert str(e.value) == "missing-fields"

def test_send_card_data_distant_payment_success():
    res = send_card_data_distant_payment({
        "name" : "John Doe",
        "number" : "4242 4242 4242 4242",
        "expiration_year" : 2025,
        "cvv" : "123",
        "expiration_month" : 9
    },10148)

    assert "credit_card" in res
    assert "transaction" in res

def test_send_card_data_distant_payment_failure():
    with pytest.raises(RequestError) as e:
        send_card_data_distant_payment({
            "name" : "John Doe",
            "number" : "4000 0000 0000 0002",
            "expiration_year" : 2025,
            "cvv" : "123",
            "expiration_month" : 9
        },10148)
    assert str(e.value) == "card-declined"
