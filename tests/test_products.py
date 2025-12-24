def test_get_all_products(client):
    """Test récupération de tous les produits"""
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_create_product(client, auth_headers):
    """Test création d'un produit"""
    product_data = {
        "name": "Nouveau Produit Test",
        "description": "Description du test",
        "price": 150.50,
        "quantity": 25,
        "min_stock": 10,
        "category_id": None
    }
    
    response = client.post("/products/", json=product_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]
    assert data["quantity"] == product_data["quantity"]
    assert "id" in data
    assert "created_at" in data

def test_get_product_by_id(client, test_product, auth_headers):
    """Test récupération d'un produit par ID"""
    response = client.get(f"/products/{test_product}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_product

def test_get_nonexistent_product(client, auth_headers):
    """Test récupération d'un produit inexistant"""
    response = client.get("/products/9999", headers=auth_headers)
    assert response.status_code == 404

def test_update_product(client, test_product, auth_headers):
    """Test mise à jour d'un produit"""
    update_data = {
        "name": "Produit Mis à Jour",
        "price": 200.00,
        "quantity": 30
    }
    
    response = client.put(
        f"/products/{test_product}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["price"] == update_data["price"]
    assert data["quantity"] == update_data["quantity"]

def test_update_nonexistent_product(client, auth_headers):
    """Test mise à jour d'un produit inexistant"""
    response = client.put(
        "/products/9999",
        json={"name": "Test"},
        headers=auth_headers
    )
    assert response.status_code == 404

def test_delete_product(client, auth_headers):
    """Test suppression d'un produit"""
    # Créer un produit à supprimer
    product = client.post(
        "/products/",
        json={"name": "To Delete", "price": 50, "quantity": 5},
        headers=auth_headers
    )
    product_id = product.json()["id"]
    
    # Supprimer
    response = client.delete(f"/products/{product_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Vérifier qu'il est supprimé
    get_response = client.get(f"/products/{product_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_delete_nonexistent_product(client, auth_headers):
    """Test suppression d'un produit inexistant"""
    response = client.delete("/products/9999", headers=auth_headers)
    assert response.status_code == 404

def test_get_low_stock_products(client, auth_headers):
    """Test récupération des produits avec stock bas"""
    response = client.get("/products/stock/low-stock?threshold=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_upload_product_image(client, test_product, auth_headers):
    """Test upload d'image pour un produit"""
    # Note: Pour tester avec un vrai fichier, vous aurez besoin d'un fichier test
    # Pour l'instant on teste juste que l'endpoint existe
    response = client.get(f"/products/upload-image/{test_product}", headers=auth_headers)
    # L'endpoint attend POST, donc GET retourne 405
    assert response.status_code == 405

def test_search_products(client):
    """Test recherche de produits"""
    response = client.get("/products/?search=test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_pagination_products(client):
    """Test pagination des produits"""
    response = client.get("/products/?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5
