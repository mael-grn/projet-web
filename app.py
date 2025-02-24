from flask import *
import logging
from database import init_database
from model.order import Order
from model.product import Product
from model.productOrder import ProductOrder
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

    # Vérification de la présence des champs nécessaires, sinon erreur 400
    if not data or 'product' not in data or 'id' not in data['product'] or 'quantity' not in data['product']:
        return {"error": "missing-fields"}, 400

    # Vérification de l'existence du produit, sinon erreur 404
    if not Product.get_or_none(Product.id == data['product']['id']):
        return {"error": "product-not-found"}, 404

    # Création de la commande et du produit de la commande
    order = Order.create()
    product_order = ProductOrder.create(quantity=data['product']['quantity'], order=order, product=Product.get_by_id(data['product']['id']))

    return {"order_link": f"/order/{order.id}"}, 302

if __name__ == "__main__":
    app.run(debug=True)

