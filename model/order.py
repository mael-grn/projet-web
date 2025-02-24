from peewee import *

db = SqliteDatabase('shop.db')

class Order(Model):
    id = AutoField(primary_key=True)
    email = CharField(null=True)
    credit_card = CharField(null=True)
    shipping_information = CharField(null=True)
    paid = BooleanField(default=False)
    transaction = CharField(null=True)
    shipping_price = FloatField(default=0)

    class Meta:
        database = db