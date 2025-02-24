from flask import Flask
import requests
import logging

from util.productUtil import clean_products

# Initialisation du logger
logging.basicConfig(
    filename='app.log',  # Fichier de log
    level=logging.INFO,  # Niveau minimal des logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Format du log
)

# Déclaration des variables
app = Flask(__name__)
logger = logging.getLogger(__name__)
products = []
SOURCE_URL = "https://dimensweb.uqac.ca/~jgnault/shops/products/"

# Au lancement de l'application
with app.app_context():
    # Chargement des données
    logger.info("Récupération des données en ligne...")
    res = requests.get(SOURCE_URL)

    # Vérification de la réponse
    if res.status_code != 200:
        # Log de l'erreur si la réponse n'est pas 200
        logger.error(f"Erreur lors de la récupération des données : code : {res.status_code} - message : {res.text}")
    else:
        # Récupération des données dans la réponse
        res_json = res.json()
        if res_json is None or res_json['products'] is None:
            # Log de l'erreur si les données sont invalides
            logger.error("Erreur lors de la récupération des données : données invalides")
        else:
            # Réussite
            logger.info("Données récupérées avec succès")
            products = res_json['products']

@app.route('/')
def get_all_products():
    return {"products": products}

if __name__ == "__main__":
    app.run(debug=True)






if __name__ == '__main__':
    app.run()
