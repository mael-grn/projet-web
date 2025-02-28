from model.order import Order
from model.productOrder import ProductOrder


def test_get_order_success(client):
    order = Order.create()
    ProductOrder.create(quantity=1, order=order, product=1)

    response = client.get(f'/order/{order.id}')
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["order"]["id"] == order.id

def test_get_order_failure(client):
    response = client.get(f'/order/{99999}')
    assert response.status_code == 404
