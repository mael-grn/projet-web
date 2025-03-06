def test_update_order_payment_success(client):
    """ Vérifie qu'une commande peut être payée avec succès """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    assert order_response.status_code == 302
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2025,
            "cvv": "123",
            "expiration_month": 9
        }
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["order"]["paid"] is True

def test_update_order_payment_declined(client):
    """ Vérifie qu'une carte refusée retourne une erreur """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "credit_card": {
            "name": "John Doe",
            "number": "4000 0000 0000 0002",  # Carte refusée
            "expiration_year": 2025,
            "cvv": "123",
            "expiration_month": 9
        }
    })
    assert response.status_code == 422  # L'API doit refuser le paiement

def test_update_order_payment_missing_card(client):
    """ Vérifie qu'un paiement sans carte est refusé """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={})
    assert response.status_code == 422  # L'API doit exiger des infos de carte

def test_update_order_payment_expired_card(client):
    """ Vérifie qu'une carte expirée est refusée """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2020,  # Carte expirée
            "cvv": "123",
            "expiration_month": 9
        }
    })
    assert response.status_code == 422

def test_update_order_payment_already_paid(client):
    """ Vérifie qu'on ne peut pas payer deux fois une commande """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    # Premier paiement réussi
    client.put(order_url, json={
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2025,
            "cvv": "123",
            "expiration_month": 9
        }
    })

    # Deuxième tentative de paiement
    response = client.put(order_url, json={
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2025,
            "cvv": "123",
            "expiration_month": 9
        }
    })
    assert response.status_code == 422  # L'API doit refuser un second paiement

def test_update_order_payment_non_existing_order(client):
    """ Vérifie qu'on ne peut pas payer une commande inexistante """
    response = client.put('/order/999999', json={
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2025,
            "cvv": "123",
            "expiration_month": 9
        }
    })
    assert response.status_code == 404  # Commande introuvable

def test_payment_without_shipping_info(client):
    """ Vérifie qu'on ne peut pas payer une commande sans email et adresse """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2025,
            "cvv": "123",
            "expiration_month": 9
        }
    })
    assert response.status_code == 422  # L'API doit exiger une adresse et un email avant paiement


def test_transaction_details_stored(client):
    """ Vérifie que les informations de transaction sont bien enregistrées après paiement """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_year": 2025,
            "cvv": "123",
            "expiration_month": 9
        }
    })
    assert response.status_code == 200
    data = response.get_json()

    assert "transaction" in data["order"]
    assert "id" in data["order"]["transaction"]
    assert data["order"]["transaction"]["success"] is True


