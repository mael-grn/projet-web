import pytest
from peewee import SqliteDatabase

from model.creditCard import CreditCard
from model.productOrder import ProductOrder
from model.order import Order
from model.product import Product
from model.shippingInfo import ShippingInfo
from model.transaction import Transaction

# Utilisation d'une base de données en mémoire pour les tests
test_db = SqliteDatabase(":memory:")


@pytest.fixture
def setup_database():
    with test_db.bind_ctx([CreditCard, ProductOrder, Order, Product, ShippingInfo, Transaction]):
        test_db.create_tables([CreditCard, ProductOrder, Order, Product, ShippingInfo, Transaction])
        yield
        test_db.drop_tables([CreditCard, ProductOrder, Order, Product, ShippingInfo, Transaction])


def test_create_productOrder(setup_database):
    credit_card = CreditCard.create(name="test", first_digits="1234", last_digits="5678", expiration_year=2028, expiration_month=9)
    shipping_info = ShippingInfo.create(country="Canada", address="123 rue du test", postal_code="G7HG7H", city="Testville", province="test_province")
    transaction = Transaction.create(id="12345", success=False, amount=100)
    order = Order.create(email="test@example.com", credit_card=credit_card, shipping_information=shipping_info, paid=False, transaction=transaction)
    product = Product.create(name="Test Product", price=20.5, in_stock=100, description="A test product", weight=1.5, image="test.jpg")
    productOrder = ProductOrder.create(order=order, product=product, quantity=11)

    assert productOrder.id is not None
    assert productOrder.order == order
    assert productOrder.product == product
    assert productOrder.quantity == 11


def test_update_productOrder(setup_database):
    product = Product.create(name="Test Product", price=20.5, in_stock=100, description="A test product", weight=1.5,
                             image="test.jpg")
    order = Order.create(email="test@example.com", paid=False)
    productOrder = ProductOrder.create(order=order, product=product, quantity=5)

    productOrder.quantity = 10
    productOrder.save()

    updated_productOrder = ProductOrder.get(ProductOrder.id == productOrder.id)
    assert updated_productOrder.quantity == 10


def test_delete_productOrder(setup_database):
    product = Product.create(name="Test Product", price=20.5, in_stock=100, description="A test product", weight=1.5,
                             image="test.jpg")
    order = Order.create(email="test@example.com", paid=False)
    productOrder = ProductOrder.create(order=order, product=product, quantity=5)

    productOrder_id = productOrder.id
    productOrder.delete_instance()

    assert not ProductOrder.select().where(ProductOrder.id == productOrder_id).exists()
