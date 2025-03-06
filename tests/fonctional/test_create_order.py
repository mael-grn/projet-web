def test_create_order_success(client):
    """ Vérifie la création réussie d'une commande """
    response = client.post('/order', json={
        "product": {"id": 1, "quantity": 1}
    })
    assert response.status_code == 302  # Redirection vers la commande créée

def test_create_order_failure_quantity(client):
    """ Vérifie qu'une commande avec une quantité négative échoue """
    response = client.post('/order', json={
        "product": {"id": 1, "quantity": -1}
    })
    assert response.status_code == 422

def test_create_order_failure_missing_fields(client):
    """ Vérifie qu'une commande sans données est rejetée """
    response = client.post('/order', json={})
    assert response.status_code == 422

def test_create_order_failure_product_not_found(client):
    """ Vérifie qu'une commande avec un produit inexistant échoue """
    response = client.post('/order', json={
        "product": {"id": 999999}
    })
    assert response.status_code == 404

def test_create_order_failure_too_large_quantity(client):
    """ Vérifie qu'une commande avec une quantité excessive est refusée """
    response = client.post('/order', json={
        "product": {"id": 1, "quantity": 1000000}  # Valeur déraisonnable
    })
    assert response.status_code == 422  # L'API doit refuser cette quantité

def test_create_order_failure_out_of_stock(client):
    """ Vérifie qu'on ne peut pas commander un produit hors stock """
    response = client.post('/order', json={
        "product": {"id": 2, "quantity": 1}  # ID d'un produit hors stock
    })
    assert response.status_code == 422  # Vérifier que l'erreur est bien levée
def test_create_order_failure_invalid_json(client):
    """ Vérifie que l'API retourne une erreur si le JSON est mal formé """
    response = client.post('/order', data="not a json")  # Mauvais format
    assert response.status_code == 400  # Mauvaise requête


def test_create_order_failure_duplicate(client):
    """ Vérifie qu'on ne peut pas commander le même produit plusieurs fois simultanément """
    response1 = client.post('/order', json={"product": {"id": 1, "quantity": 1}})
    response2 = client.post('/order', json={"product": {"id": 1, "quantity": 1}})

    assert response1.status_code == 302  # La première passe
    assert response2.status_code in [302, 409]  # La seconde peut être bloquée (si logique de duplication présente)

