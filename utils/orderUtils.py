from model.productOrder import ProductOrder

TAXE_RATE = {
    "QC": 0.15,
    "NS": 0.14,
    "ON": 0.13,
    "BC": 0.12,
    "AB": 0.05,
}

def calculate_total_price(order):
    product_orders = ProductOrder.select().where(ProductOrder.order == order)

    # Si aucun produit trouvé, retourner 0
    if not product_orders.exists():
        return 0

    # Calcul du prix total
    total_price = sum(po.product.price * po.quantity for po in product_orders)

    return total_price

def calculate_total_price_tax(order):
    # Calcul du prix total avec taxes selon la province. Si la province n'est pas dans la liste, on retourne le prix total sans taxes

    if not order.shipping_information:
        return calculate_total_price(order)

    match order.shipping_information.province:
        case "QC":
            return calculate_total_price(order) * (1 + TAXE_RATE["QC"])
        case "NS":
            return calculate_total_price(order) * (1 + TAXE_RATE["NS"])
        case "ON":
            return calculate_total_price(order) * (1 + TAXE_RATE["ON"])
        case "BC":
            return calculate_total_price(order) * (1 + TAXE_RATE["BC"])
        case "AB":
            return calculate_total_price(order) * (1 + TAXE_RATE["AB"])
        case _:
            return calculate_total_price(order)

def calculate_shipping_price(order):
    # Calcul du poids total
    total_weight = sum(po.product.weight * po.quantity for po in ProductOrder.select().where(ProductOrder.order == order))

    # Calcul du prix de la livraison
    if total_weight <= 500:
        return 5
    elif total_weight <= 2000:
        return 10
    else:
        return 25
