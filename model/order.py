from peewee import *

from model.creditCard import CreditCard
from model.shippingInfo import ShippingInfo
from model.transaction import Transaction

db = SqliteDatabase('shop.db')

class Order(Model):
    id = AutoField(primary_key=True)
    email = CharField(null=True)
    credit_card = ForeignKeyField(CreditCard, backref='orders', null=True)
    shipping_information = ForeignKeyField(ShippingInfo, backref='orders', null=True)
    paid = BooleanField(default=False)
    transaction = ForeignKeyField(Transaction, backref='orders', null=True)

    class Meta:
        database = db