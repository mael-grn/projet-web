def test_sql_injection(client):
    """ Vérifie que l'API est protégée contre l'injection SQL """
    response = client.post('/order', json={
        "product": {"id": "' OR '1'='1", "quantity": 1}
    })
    assert response.status_code == 422 or response.status_code == 400  # Doit échouer

def test_invalid_credit_card_number(client):
    """ Vérifie qu'une carte avec un mauvais numéro est rejetée """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "credit_card": {"name": "John Doe", "number": "1234", "expiration_year": 2025, "cvv": "12", "expiration_month": 9}
    })
    assert response.status_code == 422

def test_sql_injection_email(client):
    """ Vérifie que l'API est protégée contre l'injection SQL dans l'email """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "order": {"email": "' OR '1'='1@evil.com"}
    })
    assert response.status_code == 422 or response.status_code == 400  # L'API doit rejeter cette valeur

def test_credit_card_too_short(client):
    """ Vérifie qu'une carte avec un numéro trop court est rejetée """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "credit_card": {"name": "John Doe", "number": "4242", "expiration_year": 2025, "cvv": "123", "expiration_month": 9}
    })
    assert response.status_code == 422  # L'API doit détecter un numéro trop court

def test_credit_card_invalid_cvv(client):
    """ Vérifie que l'API rejette un CVV invalide """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "credit_card": {"name": "John Doe", "number": "4242 4242 4242 4242", "expiration_year": 2025, "cvv": "12", "expiration_month": 9}
    })
    assert response.status_code == 422  # Le CVV doit être de 3 chiffres

def test_credit_card_expired(client):
    """ Vérifie qu'une carte expirée est refusée """
    order_response = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    order_url = order_response.get_json()["order_link"]

    response = client.put(order_url, json={
        "credit_card": {"name": "John Doe", "number": "4242 4242 4242 4242", "expiration_year": 2020, "cvv": "123", "expiration_month": 9}
    })
    assert response.status_code == 422  # L'API doit refuser une carte expirée


def test_xss_attack(client):
    """ Vérifie que l'API protège contre les attaques XSS """
    response = client.post('/order', json={
        "product": {"id": 1, "quantity": 1},
        "comment": "<script>alert('Hacked!');</script>"
    })
    assert response.status_code == 422 or response.status_code == 400  # L'API doit rejeter les balises HTML

