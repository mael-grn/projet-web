import pytest
from peewee import SqliteDatabase

from model.product import Product

test_db = SqliteDatabase(":memory:")

@pytest.fixture
def setup_database():
    with test_db.bind_ctx([Product]):
        test_db.create_tables([Product])
        yield
        test_db.drop_tables([Product])

def test_create_product(setup_database):
    product = Product.create(name="test", in_stock=3, description="test de la description", price=20.1, weight=12.5, image="https://test_image.com")

    assert product.id is not None
    assert product.name == "test"
    assert product.in_stock == 3
    assert product.description == "test de la description"
    assert product.price == 20.1
    assert product.weight == 12.5
    assert product.image == "https://test_image.com"

def test_update_product(setup_database):
    product = Product.create(name="test", in_stock=3, description="test de la description", price=20.1, weight=12.5, image="https://test_image.com")
    product.name = "updated"
    product.save()
    updated_product = Product.get(Product.id == product.id)
    assert updated_product.name == "updated"

def test_delete_product(setup_database):
    product = Product.create(name="test", in_stock=3, description="test de la description", price=20.1, weight=12.5, image="https://test_image.com")
    product_id = product.id
    product.delete_instance()
    assert not Product.select().where(Product.id == product_id).exists()

def test_get_product(setup_database):
    product = Product.create(name="test", in_stock=3, description="test de la description", price=20.1, weight=12.5, image="https://test_image.com")
    retrieved_product = Product.get(Product.id == product.id)
    assert retrieved_product is not None
    assert retrieved_product.name == "test"
