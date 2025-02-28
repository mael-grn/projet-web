from peewee import *

db = SqliteDatabase('shop.db')

class CreditCard(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    first_digits = CharField()
    last_digits = CharField()
    expiration_year = IntegerField()
    expiration_month = IntegerField()

    class Meta:
        database = db