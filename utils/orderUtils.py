from model.productOrder import ProductOrder


def calculate_total_price(order):
    product_orders = ProductOrder.get(ProductOrder.order == order)

    price = 0
    for product_order in product_orders:
        price += product_order.product.price * product_order.quantity

    return price

def calculate_total_price_tax(order):
    tax_rate = 0.15
    return calculate_total_price(order) * (1 + tax_rate)