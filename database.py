from peewee import SqliteDatabase
from model.order import Order
from model.product import Product
from model.productOrder import ProductOrder
from model.shippingInfo import ShippingInfo

db = SqliteDatabase('shop.db')

def init_database():
    db.connect()
    # db.drop_tables([Product, ProductOrder, ShippingInfo, Order])  # Supprimer les tables
    db.create_tables([Product, ProductOrder, ShippingInfo, Order]) # Recréer les tables