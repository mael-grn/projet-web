
# Fonction qui lit nettoie les données des produits en supprimant les produits ne respectant pas les conditions
def clean_products(products):
    products = clean_products_ids(products)
    products = clean_products_attr(products)
    return products

# Fonction qui vérifie que tous les ids des produits sont uniques, sinon on supprime les doublons
def clean_products_ids(products) :
    seen_ids = set()  # Ensemble pour suivre les id déjà rencontrés
    unique_products = []  # Liste pour stocker les produits uniques

    for product in products:

        # Si l'id n'a pas été vu, on l'ajoute à la liste unique
        if product["id"] not in seen_ids:
            seen_ids.add(product["id"])
            unique_products.append(product)

    # Toutes les conditions sont remplies, on retourne True
    return unique_products

# Fonction qui vérifie que tous les produits ont les attributs suivants : id, name, in_stock, description, price, weight, image
def clean_products_attr(products):
    correct_products = []

    # On vérifie que tous les produits aient les attributs suivants
    for product in products:
        if  hasattr(product, "id") and hasattr(product, "name") and hasattr(product, "in_stock") and hasattr(product, "description") and hasattr(product, "price") and hasattr(product, "weight") and hasattr(product, "image"):
            correct_products.append(product)

    # Toutes les conditions sont remplies, on retourne True
    return correct_products
