def test_get_all_products(client):
    """ Vérifie que l'API retourne bien la liste des produits """
    response = client.get('/')
    assert response.status_code == 200
    products = response.get_json()["products"]
    assert isinstance(products, list)
    assert len(products) > 0  # Il doit y avoir au moins un produit

def test_get_all_products_structure(client):
    """ Vérifie que chaque produit a les bonnes clés (structure JSON) """
    response = client.get('/')
    assert response.status_code == 200

    products = response.get_json().get("products", [])
    assert len(products) > 0

    required_keys = {"id", "name", "in_stock", "description", "price", "weight", "image"}
    for product in products:
        assert required_keys.issubset(product.keys())  # Vérifie que chaque produit a bien toutes les clés attendues

def test_get_all_products_values(client):
    """ Vérifie que les valeurs des produits sont correctes (types et contenus non vides) """
    response = client.get('/')
    assert response.status_code == 200

    products = response.get_json().get("products", [])
    assert len(products) > 0

    for product in products:
        assert isinstance(product["id"], int) and product["id"] > 0
        assert isinstance(product["name"], str) and len(product["name"]) > 0
        assert isinstance(product["in_stock"], bool)  # Stock doit être un booléen (True/False)
        assert isinstance(product["description"], str) and len(product["description"]) > 0
        assert isinstance(product["price"], (int, float)) and product["price"] >= 0  # Prix positif
        assert isinstance(product["weight"], (int, float)) and product["weight"] >= 0  # Poids positif
        assert isinstance(product["image"], str) and len(product["image"]) > 0  # L'image doit avoir une valeur

def test_get_all_products_empty(client, mock_no_products):
    """ Vérifie que l'API retourne une liste vide si aucun produit n'est disponible """
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json() == {"products": []}  # Vérifie que la réponse est une liste vide


def test_get_all_products_fail(client, mock_server_error):
    """ Vérifie le comportement si le serveur a une erreur interne """
    response = client.get('/')
    assert response.status_code == 500  # Vérifie que l'API renvoie une erreur 500
