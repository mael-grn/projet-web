from model.order import Order
from model.productOrder import ProductOrder


def test_update_order_email_shipping_success(client):
    # Arrange
    order = Order.create()
    ProductOrder.create(quantity=1, order=order, product=1)

    # Act
    response = client.put(f'/order/{order.id}', json={
        "order" : {
            "email" : "jgnault@uqac.ca",
            "shipping_information" : {
                "country" : "Canada",
                "address" : "201, rue Président-Kennedy",
                "postal_code" : "G7X 3Y7",
                "city" : "Chicoutimi",
                "province" : "QC"
            }
        }
    })

    response_json = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_json["order"]["email"] == "jgnault@uqac.ca"
    assert response_json["order"]["shipping_information"]["country"] == "Canada"

def test_update_order_email_shipping_failure_no_email(client):
    # Arrange
    order = Order.create()
    ProductOrder.create(quantity=1, order=order, product=1)

    # Act
    response = client.put(f'/order/{order.id}', json={
        "order" : {
            "shipping_information" : {
                "country" : "Canada",
                "address" : "201, rue Président-Kennedy",
                "postal_code" : "G7X 3Y7",
                "city" : "Chicoutimi",
                "province" : "QC"
            }
        }
    })

    # Assert
    assert response.status_code == 422

def test_update_order_email_shipping_failure_no_address(client):
    # Arrange
    order = Order.create()
    ProductOrder.create(quantity=1, order=order, product=1)

    # Act
    response = client.put(f'/order/{order.id}', json={
        "order" : {
            "email" : "jgnault@uqac.ca"
        }
    })

    # Assert
    assert response.status_code == 422

def test_update_order_email_shipping_failure_missing(client):
    # Arrange
    order = Order.create()
    ProductOrder.create(quantity=1, order=order, product=1)

    # Act
    response = client.put(f'/order/{order.id}', json={
        "order" : {
            "email": "jgnault@uqac.ca",
            "shipping_information" : {
                "country" : "Canada",
                "postal_code" : "G7X 3Y7",
                "city" : "Chicoutimi",
                "province" : "QC"
            }
        }
    })

    # Assert
    assert response.status_code == 422