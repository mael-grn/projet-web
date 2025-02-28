
def test_create_order_success(client):
    response = client.post('/order', json={
        "product": {
            "id": 1,
            "quantity": 1
        }
    })
    assert response.status_code == 302

def test_create_order_failure_quantity(client):
    response = client.post('/order', json={
        "product": {
            "id": 1,
            "quantity": -1
        }
    })
    assert response.status_code == 422

def test_create_order_failure_object_incomplete(client):
    response = client.post('/order', json={
        "product": {
            "id": 1,
        }
    })
    assert response.status_code == 422

def test_create_order_failure_object_incomplete2(client):
    response = client.post('/order', json={
    })
    assert response.status_code == 422

def test_create_order_failure_product_inexistant(client):
    response = client.post('/order', json={
        "product": {
            "id": 9999999,
        }
    })
    assert response.status_code == 422