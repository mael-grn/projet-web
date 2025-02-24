class product:
    def __init__(self, name, id, in_stock, description, price, weight, image):
        self.name = name
        self.id = id
        self.in_stock = in_stock
        self.description = description
        self.price = price
        self.weight = weight
        self.image = image

    def __str__(self):
        return f"{self.name} - {self.price} (stock: {self.in_stock})"