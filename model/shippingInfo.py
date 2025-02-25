from peewee import *

db = SqliteDatabase('shop.db')

class ShippingInfo(Model):
    id = AutoField(primary_key=True)
    country = CharField()
    address = CharField()
    postal_code = CharField()
    city = CharField()
    province = CharField()

    class Meta:
        database = db