import pytest

from inf349 import app, db
from model.order import Order
from model.product import Product
from model.productOrder import ProductOrder
from model.shippingInfo import ShippingInfo
from model.creditCard import CreditCard
from model.transaction import Transaction
from controller.productUtils import load_products


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = "test_database.db"

    with app.test_client() as client:

        with app.app_context():
            db.connect()
            print("Connexion réussie à la base de données pour les tests.")
            db.create_tables([Product, ProductOrder, ShippingInfo, CreditCard, Transaction, Order], safe=True)
            load_products()
            yield client

    # Fermeture de la connexion à la base de données après les tests
    db.close()

@pytest.fixture
def mock_no_products(monkeypatch):
    def fake_select():
        return []
    monkeypatch.setattr("model.product.Product.select", fake_select)

@pytest.fixture
def mock_server_error(monkeypatch):
    from model.product import Product

    def fake_select(*args, **kwargs):
        raise Exception("Erreur serveur simulée")

    monkeypatch.setattr("model.product.Product.select", fake_select)


