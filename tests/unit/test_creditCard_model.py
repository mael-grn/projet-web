import pytest
from peewee import SqliteDatabase

from model.creditCard import CreditCard

test_db = SqliteDatabase(":memory:")

@pytest.fixture
def setup_database():
    with test_db.bind_ctx([CreditCard]):
        test_db.create_tables([CreditCard])
        yield  # Permet d'exécuter les tests
        test_db.drop_tables([CreditCard])

def test_create_creditCard(setup_database):
    creditCard = CreditCard.create(name="test", first_digits=1234, last_digits=5678, expiration_year=2028, expiration_month=11)

    assert creditCard.id is not None
    assert creditCard.name == "test"
    assert creditCard.first_digits == 1234
    assert creditCard.last_digits == 5678
    assert creditCard.expiration_year == 2028
    assert creditCard.expiration_month == 11