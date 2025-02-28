from model.shippingInfo import ShippingInfo


def create_shipping_info_entity_or_none(shipping_info_data):

    # Vérification de la présence des champs nécessaires pour l'adresse
    required_fields = ["country", "address", "postal_code", "city", "province"]
    if not all(shipping_info_data.get(field) for field in required_fields):
        return None

    # Création de l'adresse de livraison
    return ShippingInfo.create(
        country=shipping_info_data["country"],
        address=shipping_info_data["address"],
        postal_code=shipping_info_data["postal_code"],
        city=shipping_info_data["city"],
        province=shipping_info_data["province"]
    )