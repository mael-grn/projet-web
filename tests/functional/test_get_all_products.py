
def test_create_order(client):
    response = client.get('/')
    assert response.status_code == 200