from flask import *
import logging
from database import init_database
from model.order import Order
from model.product import Product
from model.shippingInfo import ShippingInfo
from utils.orderUtils import *
from utils.productUtils import load_products

# Initialisation du logger
logging.basicConfig(
    filename='app.log',  # Fichier de log
    level=logging.INFO,  # Niveau minimal des logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Format du log
)

# Déclaration des variables
app = Flask(__name__)
logger = logging.getLogger(__name__)

# Au lancement de l'application, on initialise la base de données et on charge les produits
# Avec init database, on crée les tables par rapport aux modèles
# Avec load products, on charge les produits depuis la source externe dans la base de données, même si ceux-ci existent déjà en base de données afin de les mettre à jour.
with app.app_context():
    logger.info("Initialisation de la base de données")
    init_database()
    logger.info("Initialisation des produits")
    load_products()

@app.get('/')
def get_all_products():
    logger.info("Récupération de tous les produits")
    products = Product.select().dicts()
    product_list = list(products)  # Convertir en liste de dictionnaires
    return {"products": product_list}

@app.post('/order')
def create_order():
    logger.info("Création d'une commande")

    # Récupération des données de la requête
    data = request.json

    # Vérification de la présence des champs nécessaires, sinon erreur 422
    if not data or 'product' not in data \
            or 'id' not in data['product'] \
            or 'quantity' not in data['product'] \
            or data["product"]["quantity"] <= 0:
        return {
            "errors": {
                "product" : {
                    "code": "missing-fields",
                    "name": "La création d'une commande nécessite un produit"
                }
            }
        }, 422

    product = Product.get_or_none(Product.id == data['product']['id'])

    # Vérification de l'existence du produit, sinon erreur 404
    if not product:
        return {"error": "product-not-found"}, 404

    # Vérification de la quantité en stock, sinon erreur 422
    if not product.in_stock:
        return {
            "errors" : {
                "product": {
                    "code": "out-of-inventory",
                    "name": "Le produit demandé n'est pas en inventaire"
                }
            }
        }, 422

    # Création de la commande et du produit de la commande
    order = Order.create()
    ProductOrder.create(quantity=data['product']['quantity'], order=order, product=Product.get_by_id(data['product']['id']))

    return {"order_link": f"/order/{order.id}"}, 302

@app.get('/order/<int:order_id>')
def get_order(order_id):
    logger.info(f"Récupération de la commande {order_id}")

    # Récupération de la commande
    order = Order.get_or_none(Order.id == order_id)

    # Vérification de l'existence de la commande, sinon erreur 404
    if not order:
        return {"error": "order-not-found"}, 404

    # Récupération des produits de la commande
    product_order_res = ProductOrder.select().where(ProductOrder.order == order)
    product_order = list(product_order_res)

    # Si aucun produit n'a été attribué à la commande
    if len(product_order) == 0:
        return {"error": "order-empty"}, 404

    # Si la commande a plus d'un seul produit
    if len(product_order) > 1:
        return {"error": "multiple-products"}, 500

    # Conversion en dictionnaire
    order_data = order.__data__

    # Ajout des propriétés manquantes
    order_data["product"] = {
        "id": product_order[0].product.id,
        "quantity": product_order[0].quantity,
    }
    order_data["total_price"] = calculate_total_price(order)
    order_data['total_price_tax'] = calculate_total_price_tax(order)
    order_data['shipping_price'] = calculate_shipping_price(order)
    if order.shipping_information:
        order_data['shipping_information'] = order.shipping_information.__data__

    return order_data

@app.put('/order/<int:order_id>')
def update_order(order_id):
    logger.info(f"Mise à jour de la commande {order_id}")

    # Récupération de la commande
    order = Order.get_or_none(Order.id == order_id)

    # Vérification de l'existence de la commande, sinon erreur 404
    if not order:
        return {"error": "order-not-found"}, 404

    # Récupération des données de la requête
    data = request.json

    if not data or not "order" in data:
        return {
            "errors": {
                "order": {
                    "code": "missing-fields",
                    "name": "La mise à jour d'une commande nécessite des informations"
                }
            }
        }, 422

    # Vérification de la présence des champs nécessaires pour l'email, sinon erreur 422
    if not "email" in data["order"]:
        return {
            "errors": {
                "order": {
                    "code": "missing-fields",
                    "name": "La mise à jour d'une commande nécessite un email"
                }
            }
        }, 422

    # Vérification de la présence des champs nécessaires pour l'adresse, sinon erreur 422
    if not "shipping_information" in data["order"] \
            or not "country" in data["order"]["shipping_information"] \
            or not "address" in data["order"]["shipping_information"] \
            or not "postal_code" in data["order"]["shipping_information"] \
            or not "city" in data["order"]["shipping_information"] \
            or not "province" in data["order"]["shipping_information"]:
        return {
            "errors": {
                "order": {
                    "code": "missing-fields",
                    "name": "La mise à jour d'une commande nécessite des informations de livraison"
                }
            }
        }, 422

    # Création de l'adresse de livraison
    shipping_info = ShippingInfo.create(
        country= data["order"]["shipping_information"]["country"],
        address= data["order"]["shipping_information"]["address"],
        postal_code= data["order"]["shipping_information"]["postal_code"],
        city= data["order"]["shipping_information"]["city"],
        province= data["order"]["shipping_information"]["province"]
    )

    # Mise à jour de la commande
    order.email = data["order"]["email"]
    order.shipping_information = shipping_info

    # Sauvegarde de la commande
    order.save()

    return get_order(order_id)


if __name__ == "__main__":
    app.run(debug=True)

