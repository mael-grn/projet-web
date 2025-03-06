import pytest
from peewee import SqliteDatabase

from model.order import Order
from model.creditCard import CreditCard
from model.transaction import Transaction
from model.shippingInfo import ShippingInfo

# Création de la base de données temporaire
test_db = SqliteDatabase(":memory:")

@pytest.fixture
def setup_database():
    with test_db.bind_ctx([CreditCard, ShippingInfo, Transaction, Order]):
        test_db.create_tables([CreditCard, ShippingInfo, Transaction, Order])
        yield
        test_db.drop_tables([CreditCard, ShippingInfo, Transaction, Order])

def test_create_order(setup_database):
    credit_card = CreditCard.create(name="test", first_digits="1234", last_digits="5678", expiration_year=2028, expiration_month=9)
    shipping_info = ShippingInfo.create(country="Canada", address="123 rue du test", postal_code="G7HG7H", city="Testville", province="test_province")
    transaction = Transaction.create(id=12345, success=False, amount=100)

    order = Order.create(
        email="test@example.com",
        credit_card=credit_card,
        shipping_information=shipping_info,
        paid=False,
        transaction=transaction
    )

    assert order.id is not None
    assert order.email == "test@example.com"
    assert order.credit_card == credit_card
    assert order.shipping_information == shipping_info
    assert order.transaction == transaction
    assert order.paid is False

def test_order_payment_status(setup_database):
    transaction = Transaction.create(id=12345678, amount=50, success=False)
    order = Order.create(email="client@test.com", transaction=transaction, paid=False)

    order.paid = True
    order.save()

    updated_order = Order.get(Order.id == order.id)
    assert updated_order.paid is True

def test_get_order(setup_database):
    transaction = Transaction.create(id='98765', amount=75, success=True)
    order = Order.create(email="retrieve@test.com", transaction=transaction, paid=True)

    retrieved_order = Order.get(Order.email == "retrieve@test.com")
    assert retrieved_order is not None
    assert retrieved_order.transaction == transaction
    assert retrieved_order.paid is True

def test_update_order_info(setup_database):
    transaction = Transaction.create(id='56789', amount=200, success=True)
    order = Order.create(email="update@test.com", transaction=transaction, paid=False)

    order.email = "updated@test.com"
    order.save()

    updated_order = Order.get(Order.id == order.id)
    assert updated_order.email == "updated@test.com"

def test_delete_order(setup_database):
    transaction = Transaction.create(id=54321, amount=120, success=True)
    order = Order.create(email="delete@test.com", transaction=transaction, paid=True)
    order_id = order.id

    order.delete_instance()

    with pytest.raises(Order.DoesNotExist):
        Order.get(Order.id == order_id)
