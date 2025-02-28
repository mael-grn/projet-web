from peewee import *

db = SqliteDatabase('shop.db')

class Transaction(Model):
    id = CharField(primary_key=True)
    success = BooleanField()
    amount = IntegerField()


    class Meta:
        database = db