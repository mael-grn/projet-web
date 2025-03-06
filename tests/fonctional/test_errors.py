def test_create_order_invalid_product(client):
    """ Vérifie qu'une commande avec un produit invalide retourne 404 """
    response = client.post('/order', json={"product": {"id": 999999}})
    assert response.status_code == 404

def test_payment_already_paid_order(client):
    """ Vérifie qu'on ne peut pas payer deux fois une commande """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    client.put(order_url, json={
        "credit_card": {"name": "John Doe", "number": "4242 4242 4242 4242", "expiration_year": 2025, "cvv": "123", "expiration_month": 9}
    })

    response = client.put(order_url, json={
        "credit_card": {"name": "John Doe", "number": "4242 4242 4242 4242", "expiration_year": 2025, "cvv": "123", "expiration_month": 9}
    })
    assert response.status_code == 422

def test_payment_missing_credit_card(client):
    """ Vérifie qu'un paiement sans carte de crédit est rejeté """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={})
    assert response.status_code == 422  # L'API doit exiger une carte de crédit

def test_payment_declined_card(client):
    """ Vérifie qu'une carte refusée retourne une erreur """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "credit_card": {"name": "John Doe", "number": "4000 0000 0000 0002", "expiration_year": 2025, "cvv": "123", "expiration_month": 9}
    })
    assert response.status_code == 422  # Vérifie que l'API détecte une carte refusée
def test_create_order_invalid_json(client):
    """ Vérifie qu'un JSON mal formé retourne une erreur 400 """
    response = client.post('/order', data="not a json")  # Mauvais format
    assert response.status_code == 400  # Mauvaise requête

def test_update_non_existing_order(client):
    """ Vérifie qu'on ne peut pas mettre à jour une commande inexistante """
    response = client.put('/order/999999', json={"order": {"email": "test@example.com"}})
    assert response.status_code == 404  # Vérifie que l'API retourne une erreur


def test_delete_non_existing_order(client):
    """ Vérifie que la suppression d'une commande inexistante retourne 404 """
    response = client.delete('/order/999999')
    assert response.status_code == 404  # Vérifie que l'API ne trouve pas la commande

