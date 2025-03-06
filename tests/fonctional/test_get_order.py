def test_get_order_success(client):
    """ Vérifie la récupération d'une commande existante """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    assert order_response.status_code == 302
    order_url = order_response.get_json()["order_link"]

    response = client.get(order_url)
    assert response.status_code == 200
    assert response.get_json()["order"]["product"]["id"] == 1

def test_get_order_failure(client):
    """ Vérifie qu'une commande inexistante retourne 404 """
    response = client.get('/order/99999')
    assert response.status_code == 404

def test_get_order_no_product(client):
    """ Vérifie qu'une commande sans produit retourne une erreur appropriée """
    order_response = client.post('/order', json={})  # Création d'une commande vide
    assert order_response.status_code == 422  # Devrait échouer à la création

def test_get_order_cancelled(client):
    """ Vérifie qu'une commande annulée retourne une erreur appropriée """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    client.delete(order_url)  # Supposons que l'API permette d'annuler une commande
    response = client.get(order_url)
    assert response.status_code == 404  # La commande ne doit plus être accessible

def test_get_order_after_payment(client):
    """ Vérifie qu'une commande payée contient bien les détails de la transaction """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    payment_response = client.put(order_url, json={
        "credit_card": {"name": "John Doe", "number": "4242 4242 4242 4242", "expiration_year": 2025, "cvv": "123", "expiration_month": 9}
    })
    assert payment_response.status_code == 200

    response = client.get(order_url)
    assert response.status_code == 200
    order_data = response.get_json()["order"]
    assert order_data["paid"] is True
    assert "transaction" in order_data  # Vérifie que la transaction est enregistrée

def test_get_order_missing_info(client):
    """ Vérifie qu'une commande sans email ou adresse d'expédition est toujours récupérable """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.get(order_url)
    assert response.status_code == 200
    order_data = response.get_json()["order"]
    assert order_data["email"] is None  # L'email ne doit pas être obligatoire à ce stade
    assert order_data["shipping_information"] == {}  # L'adresse ne doit pas être obligatoire

def test_order_taxes_by_province(client):
    """ Vérifie que les taxes sont correctement appliquées selon la province """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
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
    assert data["order"]["total_price_tax"] == data["order"]["total_price"] * 1.15  # Québec = 15% de taxe


def test_shipping_price_calculation(client):
    """ Vérifie que les frais d'expédition sont calculés correctement selon le poids total """
    order_response = client.post('/order',
                                 json={"product": {"id": 1, "quantity": 2}})  # Supposons que chaque produit pèse 500g
    order_url = order_response.get_json()["order_link"]

    response = client.get(order_url)
    assert response.status_code == 200
    data = response.get_json()

    assert data["order"]["shipping_price"] == 10  # 2 produits de 500g → 1kg → 10$
