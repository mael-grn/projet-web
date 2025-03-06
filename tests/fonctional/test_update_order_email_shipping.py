def test_update_order_email_shipping_success(client):
    """ Vérifie la mise à jour de l'email et de l'adresse d'expédition """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    assert order_response.status_code == 302
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "order": {
            "email": "user@example.com",
            "shipping_information": {
                "country": "Canada",
                "address": "123 rue Exemple",
                "postal_code": "A1B 2C3",
                "city": "Montréal",
                "province": "QC"
            }
        }
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["order"]["email"] == "user@example.com"

def test_update_order_missing_email(client):
    """ Vérifie qu'une mise à jour sans email échoue """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={"order": {"shipping_information": {}}})
    assert response.status_code == 422

def test_update_order_missing_address(client):
    """ Vérifie qu'une mise à jour sans adresse complète échoue """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "order": {
            "email": "user@example.com",
            "shipping_information": {
                "country": "Canada"
            }
        }
    })
    assert response.status_code == 422  # L'API doit exiger une adresse complète

def test_update_order_invalid_email(client):
    """ Vérifie que l'API rejette un email invalide """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "order": {
            "email": "not-an-email",
            "shipping_information": {
                "country": "Canada",
                "address": "123 rue Exemple",
                "postal_code": "A1B 2C3",
                "city": "Montréal",
                "province": "QC"
            }
        }
    })
    assert response.status_code == 422  # L'API doit refuser un email invalide

def test_update_non_existing_order(client):
    """ Vérifie qu'on ne peut pas mettre à jour une commande inexistante """
    response = client.put('/order/999999', json={
        "order": {
            "email": "user@example.com",
            "shipping_information": {
                "country": "Canada",
                "address": "123 rue Exemple",
                "postal_code": "A1B 2C3",
                "city": "Montréal",
                "province": "QC"
            }
        }
    })
    assert response.status_code == 404  # Vérifie que l'API retourne une erreur

def test_update_paid_order(client):
    """ Vérifie qu'une commande déjà payée ne peut pas être modifiée """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    # Paiement de la commande
    client.put(order_url, json={
        "credit_card": {"name": "John Doe", "number": "4242 4242 4242 4242", "expiration_year": 2025, "cvv": "123", "expiration_month": 9}
    })

    # Tentative de modification après paiement
    response = client.put(order_url, json={
        "order": {
            "email": "new-email@example.com",
            "shipping_information": {
                "country": "Canada",
                "address": "456 rue Nouvelle",
                "postal_code": "A1B 2C3",
                "city": "Québec",
                "province": "QC"
            }
        }
    })
    assert response.status_code == 422  # Modification interdite après paiement

