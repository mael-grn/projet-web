from peewee import SqliteDatabase
from model.order import Order
from model.product import Product
from model.productOrder import ProductOrder

db = SqliteDatabase('shop.db')

def init_database():
    db.connect()
    db.drop_tables([Product, ProductOrder, Order])  # Supprimer les tables
    db.create_tables([Product, ProductOrder, Order]) # Recréer les tables