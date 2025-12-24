def test_get_all_movements(client, auth_headers):
    """Test récupération de tous les mouvements"""
    response = client.get("/movements/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_create_movement_in(client, test_product, auth_headers):
    """Test création d'une entrée de stock"""
    movement_data = {
        "product_id": test_product,
        "type": "in",
        "quantity": 15
    }
    
    response = client.post("/movements/", json=movement_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == test_product
    assert data["type"] == "in"
    assert data["quantity"] == 15
    assert "id" in data
    assert "timestamp" in data

def test_create_movement_out(client, test_product, auth_headers):
    """Test création d'une sortie de stock"""
    # D'abord ajouter du stock
    client.post("/movements/", 
        json={"product_id": test_product, "type": "in", "quantity": 50},
        headers=auth_headers
    )
    
    # Puis sortie
    movement_data = {
        "product_id": test_product,
        "type": "out",
        "quantity": 20
    }
    
    response = client.post("/movements/", json=movement_data, headers=auth_headers)
    assert response.status_code == 200

def test_create_movement_insufficient_stock(client, test_product, auth_headers):
    """Test sortie avec stock insuffisant"""
    movement_data = {
        "product_id": test_product,
        "type": "out",
        "quantity": 1000  # Trop grand
    }
    
    response = client.post("/movements/", json=movement_data, headers=auth_headers)
    assert response.status_code == 400

def test_create_movement_nonexistent_product(client, auth_headers):
    """Test mouvement pour produit inexistant"""
    movement_data = {
        "product_id": 9999,
        "type": "in",
        "quantity": 10
    }
    
    response = client.post("/movements/", json=movement_data, headers=auth_headers)
    assert response.status_code == 404

def test_get_movement_history(client, auth_headers):
    """Test historique des mouvements"""
    response = client.get("/movements/history", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_movement_stats(client, auth_headers):
    """Test statistiques des mouvements"""
    response = client.get("/movements/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "total_stock" in data
    assert "total_entries" in data
    assert "total_exits" in data

def test_filter_movements_by_type(client, auth_headers):
    """Test filtrage des mouvements par type"""
    response = client.get("/movements/movements/?type=in", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_movement_updates_product_quantity(client, test_product, auth_headers):
    """Test que le mouvement met à jour la quantité du produit"""
    # Quantité initiale
    initial_product = client.get(f"/products/{test_product}", headers=auth_headers).json()
    initial_quantity = initial_product["quantity"]
    
    # Ajouter du stock
    client.post("/movements/", 
        json={"product_id": test_product, "type": "in", "quantity": 10},
        headers=auth_headers
    )
    
    # Vérifier nouvelle quantité
    updated_product = client.get(f"/products/{test_product}", headers=auth_headers).json()
    assert updated_product["quantity"] == initial_quantity + 10
    
    # Retirer du stock
    client.post("/movements/", 
        json={"product_id": test_product, "type": "out", "quantity": 5},
        headers=auth_headers
    )
    
    # Vérifier quantité finale
    final_product = client.get(f"/products/{test_product}", headers=auth_headers).json()
    assert final_product["quantity"] == initial_quantity + 5
