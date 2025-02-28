from flask import *
import logging
from peewee import SqliteDatabase
from model.order import Order
from model.product import Product
from model.productOrder import ProductOrder
from model.requestError import RequestError
from utils.orderUtils import calculate_total_price, calculate_total_price_tax, calculate_shipping_price, \
    update_order_shipping_and_email, update_order_payment
from utils.productUtils import load_products

# Initialisation du logger
logging.basicConfig(
    filename='app.log',  # Fichier de log
    level=logging.INFO,  # Niveau minimal des logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Format du log
)

# Initialisation de l'application Flask
app = Flask(__name__)
logger = logging.getLogger(__name__)

# Configuration de la base de données (ex: SQLite)
DATABASE = "database.db"
db = SqliteDatabase(DATABASE)

# Fonction pour initialiser la base de données
def init_db():
    from model.creditCard import CreditCard
    from model.order import Order
    from model.product import Product
    from model.productOrder import ProductOrder
    from model.shippingInfo import ShippingInfo
    from model.transaction import Transaction
    db.connect()
    db.create_tables([Product, ProductOrder, ShippingInfo, CreditCard, Transaction, Order], safe=True)
    logger.info("Initialisation des produits")
    load_products()
    db.close()
    logger.info("Base de données initialisée")

# Commande Flask pour initialiser la base de données
@app.cli.command("init-db")
def init_db_command():
    """Initialise la base de données."""
    init_db()
    print("Base de données créée avec succès.")

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
        logger.error("La requête ne contient pas les champs nécessaires")
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
        logger.error("Le produit demandé n'existe pas")
        return {"error": "product-not-found"}, 404

    # Vérification de la quantité en stock, sinon erreur 422
    if not product.in_stock:
        logger.error("Le produit demandé n'est pas en inventaire")
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

    logger.info(f"Commande {order.id} créée avec succès")
    return {"order_link": f"/order/{order.id}"}, 302

@app.get('/order/<int:order_id>')
def get_order(order_id):
    logger.info(f"Récupération de la commande {order_id}")

    # Récupération de la commande
    order = Order.get_or_none(Order.id == order_id)

    # Vérification de l'existence de la commande, sinon erreur 404
    if not order:
        logger.error("La commande demandée n'existe pas")
        return {"error": "order-not-found"}, 404

    # Récupération des produits de la commande
    product_order_res = ProductOrder.select().where(ProductOrder.order == order)
    product_order = list(product_order_res)

    # Si aucun produit n'a été attribué à la commande
    if len(product_order) == 0:
        logger.error("La commande est vide")
        return {"error": "order-empty"}, 404

    # Si la commande a plus d'un seul produit
    if len(product_order) > 1:
        logger.error("La commande contient plusieurs produits")
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

    logger.info(f"Commande {order_id} récupérée avec succès")
    return {"order": order_data}

@app.put('/order/<int:order_id>')
def update_order(order_id):
    logger.info(f"Mise à jour de la commande {order_id}")

    # Récupération de la commande
    order = Order.get_or_none(Order.id == order_id)

    # Vérification de l'existence de la commande, sinon erreur 404
    if not order:
        logger.error("La commande demandée n'existe pas")
        return {"error": "order-not-found"}, 404

    # Récupération des données de la requête
    data = request.json

    if not data:
        logger.error("La requête ne contient pas les champs nécessaires")
        return {
            "errors": {
                "order": {
                    "code": "missing-fields",
                    "name": "La mise à jour d'une commande nécessite des informations"
                }
            }
        }, 422

    # On redirige vers la fonction appropriée en fonction des données reçues
    if "order" in data and "email" in data["order"] and "shipping_information" in data["order"] and not "credit_card" in data:

        logger.info(f"Mise à jour de l'adresse et de l'email de la commande {order_id}")

        # Mise à jour des données
        try:
            update_order_shipping_and_email(order, data)
            # Retourne la commande complète
            logger.info(f"Commande {order_id} mise à jour avec succès")
            return get_order(order.id)

        except RequestError as e:
            logger.error(f"Erreur lors de la mise à jour de la commande {order_id}")
            return {
                "errors": {
                    "order": {
                        "code": str(e),
                        "name": e.details
                    }
                }
            }, e.code

    elif "credit_card" in data and not "order" in data:

        logger.info(f"Mise à jour de la carte de crédit de la commande {order_id}")

        # Mise à jour des données
        try:
            update_order_payment(order, data)
            # Retourne la commande complète
            logger.info(f"Commande {order_id} mise à jour avec succès")
            return get_order(order.id)

        except RequestError as e:
            logger.error(f"Erreur lors de la mise à jour de la commande {order_id}")
            return {
                "errors": {
                    "order": {
                        "code": str(e),
                        "name": e.details
                    }
                }
            }, e.code
    else:
        logger.error("La requête ne contient pas les champs nécessaires")
        return {
            "errors": {
                "order": {
                    "code": "missing-fields",
                    "name": "La mise à jour d'une commande nécessite des informations d'une adresse et d'un email, ou d'une carte de crédit"
                }
            }
        }, 422

if __name__ == "__main__":
    app.run(debug=True)
