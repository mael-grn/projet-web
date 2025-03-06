import requests
from model.product import Product

SOURCE_URL = "https://dimensweb.uqac.ca/~jgnault/shops/products/"

def get_products_from_source():
    # Chargement des données
    res = requests.get(SOURCE_URL)

    # Vérification de la réponse
    if res.status_code != 200:
        # La réponse n'est pas 200.
        raise f"Erreur lors de la récupération des données : code : {res.status_code} - message : {res.text}"
    else:
        # Récupération des données dans la réponse
        res_json = res.json()
        if res_json is None or res_json['products'] is None:
            # Les données sont invalides.
            raise "Erreur lors de la récupération des données : données invalides"
        else:
            # Réussite
            return res_json['products']

def upsert_product_from_json(json):
    # Test d'insertion de produit
    product, created = Product.get_or_create(id=json['id'], defaults=json)

    # Si le produit n'a pas été inséré, alors il existe déjà et on le met à jour
    if not created:
        # Mise à jour des données
        product.name = json['name']
        product.in_stock = json['in_stock']
        product.description = json['description']
        product.price = json['price']
        product.weight = json['weight']
        product.image = json['image']
        product.save()

def load_products():
    # Récupération des produits
    products_json = get_products_from_source()

    # Insertion des produits
    for product_json in products_json:
        upsert_product_from_json(product_json)
