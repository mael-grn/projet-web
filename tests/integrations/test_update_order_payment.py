from model.order import Order
from model.productOrder import ProductOrder
from model.shippingInfo import ShippingInfo


def test_update_order_email_shipping_success(client):
    # Arrange
    shipping = ShippingInfo.create(country="Canada", address="201, rue Président-Kennedy", postal_code="G7X 3Y7", city="Chicoutimi", province="QC")
    order = Order.create(email="jgnault@uqac.ca", shipping_information=shipping)
    ProductOrder.create(quantity=1, order=order, product=1)

    # Act
    response = client.put(f'/order/{order.id}', json={
        "credit_card" : {
            "name" : "John Doe",
            "number" : "4242 4242 4242 4242",
            "expiration_year" : 2025,
            "cvv" : "123",
            "expiration_month" : 9
        }
    })

    response_json = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_json["order"]["paid"] == True
    assert response_json["order"]["credit_card"]["name"] == "John Doe"
    assert response_json["order"]["credit_card"]["first_digits"] == "4242"
    assert response_json["order"]["transaction"]["success"] == True


# test securite injesction sqlqui il faut bla de ce que je vois la transformationde l'écriture manuscrite en texte marche bien mais pas par faitement bientest les injections s•l