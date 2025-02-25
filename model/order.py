from peewee import *

from model.shippingInfo import ShippingInfo

db = SqliteDatabase('shop.db')

class Order(Model):
    id = AutoField(primary_key=True)
    email = CharField(null=True)
    credit_card = CharField(null=True)
    shipping_information = ForeignKeyField(ShippingInfo, backref='orders', null=True)
    paid = BooleanField(default=False)
    transaction = CharField(null=True)

    class Meta:
        database = db