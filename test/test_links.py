LINK = {"original_url": "https://example.com/long-url", "short_name": "exmpl"}


def test_create_link(client):
    response = client.post("/api/links", json=LINK)
    assert response.status_code == 201
    assert response.json()["original_url"] == LINK["original_url"]
    assert response.json()["short_name"] == LINK["short_name"]


def test_create_duplicate(client):
    client.post("/api/links", json=LINK)
    response = client.post("/api/links", json=LINK)
    assert response.status_code == 409
    assert "detail" in response.json()


def test_create_invalid(client):
    response = client.post("/api/links", json={"original_url": LINK["original_url"]})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_get_link(client):
    created = client.post("/api/links", json=LINK).json()
    response = client.get(f"/api/links/{created['id']}")
    assert response.status_code == 200
    assert response.json()["original_url"] == LINK["original_url"]
    assert response.json()["short_name"] == LINK["short_name"]


def test_get_missing(client):
    response = client.get("/api/links/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Link not found"}


def test_list_links(client):
    client.post("/api/links", json=LINK | {"short_name": "other"})
    client.post("/api/links", json=LINK)
    response = client.get("/api/links")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_link(client):
    created = client.post("/api/links", json=LINK).json()
    new = {"original_url": "https://new.example.com", "short_name": "other"}
    response = client.put(f"/api/links/{created['id']}", json=new)
    assert response.status_code == 200
    assert response.json()["original_url"] == new["original_url"]
    assert response.json()["short_name"] == new["short_name"]


def test_update_missing(client):
    response = client.put("/api/links/999", json=LINK)
    assert response.status_code == 404


def test_delete_link(client):
    created = client.post("/api/links", json=LINK).json()
    deleted = client.delete(f"/api/links/{created['id']}")
    assert deleted.status_code == 204
    assert deleted.text == ""


def test_redirect(client):
    client.post("/api/links", json=LINK)
    response = client.get(f"/r/{LINK['short_name']}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == LINK["original_url"]


def test_redirect_missing(client):
    response = client.get("/r/nope")
    assert response.status_code == 404
