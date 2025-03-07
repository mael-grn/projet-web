from flask import *
import logging
from peewee import SqliteDatabase
from model.order import Order
from model.product import Product
from model.productOrder import ProductOrder
from model.requestError import RequestError
from controller.orderUtils import calculate_total_price, calculate_total_price_tax, calculate_shipping_price, \
    update_order_shipping_and_email, update_order_payment
from controller.productUtils import load_products
import re
import peewee

from model.transaction import Transaction

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

    try:
        products = Product.select()
        product_list = [
            {
                "id": p.id,
                "name": p.name,
                "in_stock": bool(p.in_stock),
                "description": p.description,
                "price": p.price,
                "weight": p.weight,
                "image": p.image
            }
            for p in products
        ]
        return {"products": product_list}, 200
    except Exception as e:
        print(f"DEBUG: Erreur interne capturée dans get_all_products - {str(e)}")
        return {"error": "internal-server-error"}, 500



def contains_xss(value):
    return bool(re.search(r'<script.*?>.*?</script>', value, re.IGNORECASE))

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

@app.post('/order')
def create_order():
    logger.info("Création d'une commande")
    # Récupération des données de la requête
    if not request.content_type or "application/json" not in request.content_type:
        return {
            "errors": {
                "request": {
                    "code": "invalid-content-type",
                    "name": "Le Content-Type doit être application/json"
                }
            }
        }, 400

    for key, value in request.json.items():
        if isinstance(value, str) and contains_xss(value):
            return {
                "errors": {
                    "request": {
                        "code": "xss-detected",
                        "name": "Tentative d'injection XSS détectée"
                    }
                }
            }, 400

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
    try:
        product_id = int(data["product"]["id"])  # 🔹 Convertir pour éviter l'injection SQL
    except ValueError:
        return {
            "errors": {
                "product": {
                    "code": "invalid-product-id",
                    "name": "L'ID du produit doit être un entier valide"
                }
            }
        }, 400
    product = Product.get_or_none(Product.id == data['product']['id'])
    # Vérification de l'existence du produit, sinon erreur 404
    if not product:
        logger.error("Le produit demandé n'existe pas")
        return {"error": "product-not-found"}, 404
    if product.in_stock < data["product"]["quantity"]:
        logger.error("La quantité demandée dépasse le stock disponible")
        return {
            "errors": {
                "product": {
                    "code": "excessive-quantity",
                    "name": "La quantité demandée dépasse le stock disponible"
                }
            }
        }, 422
    # Vérification de la quantité en stock, sinon erreur 422
    if product.in_stock <= 0:  # 🔹 Vérifie explicitement que le produit est hors stock
        logger.error("Le produit demandé n'est pas en inventaire")
        return {
            "errors": {
                "product": {
                    "code": "out-of-inventory",
                    "name": "Le produit demandé n'est pas en inventaire"
                }
            }
        }, 422

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
    order = Order.select(Order, Transaction).join(Transaction, peewee.JOIN.LEFT_OUTER).where(Order.id == order_id).first()

    # Vérification de l'existence de la commande, sinon erreur 404
    if not order:
        logger.error("La commande demandée n'existe pas")
        return {"error": "order-not-found"}, 404

    # Récupération des produits de la commande
    product_order_res = ProductOrder.select().where(ProductOrder.order == order)
    product_order = list(product_order_res)
    print(f"product_order : {product_order}")
    # Si aucun produit n'a été attribué à la commande
    if len(product_order) == 0:
        logger.error("La commande est vide")
        return {"error": "order-empty"}, 404

    # Si la commande a plus d'un seul produit
    if len(product_order) > 1:
        logger.error("La commande contient plusieurs produits")
        return {"error": "multiple-products"}, 422

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
    order_data['shipping_information'] = order.shipping_information.__data__ if order.shipping_information else {}
    if order.transaction :
        order_data["transaction"] = {
            "id": order.transaction.id,
            "success": order.transaction.success,
            "amount": order.transaction.amount
        }

    logger.info(f"Commande {order_id} récupérée avec succès")
    if not order.transaction:
        order.transaction = None

    return {"order": order_data}

@app.delete('/order/<int:order_id>')
def delete_order(order_id):
    logger.info(f"Suppression de la commande {order_id}")

    # Récupération de la commande
    order = Order.get_or_none(Order.id == order_id)

    # Vérification de l'existence de la commande, sinon erreur 404
    if not order:
        logger.error("La commande demandée n'existe pas")
        return {"error": "order-not-found"}, 404

    # Suppression de la commande
    order.delete_instance()
    logger.info(f"Commande {order_id} supprimée avec succès")

    return {"message": "Commande supprimée avec succès"}, 200

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
        print(f"DEBUG: Raison du 422 - {order.__data__}")
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
        print(f"DEBUG: Raison du 422 - {order.__data__}")
        if not is_valid_email(request.json["order"]["email"]):
            return {
                "errors": {
                    "email": {
                        "code": "invalid-email",
                        "name": "L'email fourni est invalide"
                    }
                }
            }, 422
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
        print(f"DEBUG: Raison du 422 - {order.__data__}")
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
        print(f"DEBUG: Raison du 422 - {order.__data__}")
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
