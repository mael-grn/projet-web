import pytest
from peewee import SqliteDatabase
from model.shippingInfo import ShippingInfo

test_db = SqliteDatabase(':memory:')


@pytest.fixture
def setup_database():
    test_db.bind([ShippingInfo], bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables([ShippingInfo])
    yield
    test_db.drop_tables([ShippingInfo])
    test_db.close()


def test_create_shipping_info(setup_database):
    shipping = ShippingInfo.create(
        country="Canada",
        address="123 Rue Principale",
        postal_code="G1A 0A1",
        city="Québec",
        province="QC"
    )

    assert shipping.id is not None
    assert shipping.country == "Canada"
    assert shipping.address == "123 Rue Principale"
    assert shipping.postal_code == "G1A 0A1"
    assert shipping.city == "Québec"
    assert shipping.province == "QC"


def test_retrieve_shipping_info(setup_database):
    ShippingInfo.create(
        country="France",
        address="45 Avenue des Champs",
        postal_code="75008",
        city="Paris",
        province="Île-de-France"
    )

    shipping = ShippingInfo.get(ShippingInfo.city == "Paris")

    assert shipping is not None
    assert shipping.country == "France"
    assert shipping.address == "45 Avenue des Champs"


def test_update_shipping_info(setup_database):
    shipping = ShippingInfo.create(
        country="Belgique",
        address="10 Rue Royale",
        postal_code="1000",
        city="Bruxelles",
        province="Bruxelles"
    )

    shipping.address = "12 Rue Royale"
    shipping.save()
    updated_shipping = ShippingInfo.get(ShippingInfo.id == shipping.id)

    assert updated_shipping.address == "12 Rue Royale"


def test_delete_shipping_info(setup_database):
    shipping = ShippingInfo.create(
        country="Suisse",
        address="5 Chemin du Lac",
        postal_code="1201",
        city="Genève",
        province="Genève"
    )

    shipping_id = shipping.id
    shipping.delete_instance()

    with pytest.raises(ShippingInfo.DoesNotExist):
        ShippingInfo.get(ShippingInfo.id == shipping_id)
