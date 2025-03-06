import pytest
from peewee import SqliteDatabase
from model.transaction import Transaction

db = SqliteDatabase(':memory:')

@pytest.fixture
def setup_database():
    db.bind([Transaction], bind_refs=False, bind_backrefs=False)
    db.connect()
    db.create_tables([Transaction])
    yield db
    db.drop_tables([Transaction])
    db.close()

def test_create_transaction(setup_database):
    transaction = Transaction.create(id="123ABC", success=True, amount=100)
    assert transaction.id == "123ABC"
    assert transaction.success is True
    assert transaction.amount == 100

def test_retrieve_transaction(setup_database):
    Transaction.create(id="123ABC", success=True, amount=100)
    transaction = Transaction.get(Transaction.id == "123ABC")
    assert transaction is not None
    assert transaction.success is True

def test_update_transaction(setup_database):
    transaction = Transaction.create(id="123ABC", success=True, amount=100)
    transaction.success = False
    transaction.save()
    updated_transaction = Transaction.get(Transaction.id == "123ABC")
    assert updated_transaction.success is False

def test_delete_transaction(setup_database):
    transaction = Transaction.create(id="123ABC", success=True, amount=100)
    transaction.delete_instance()
    with pytest.raises(Transaction.DoesNotExist):
        Transaction.get(Transaction.id == "123ABC")
