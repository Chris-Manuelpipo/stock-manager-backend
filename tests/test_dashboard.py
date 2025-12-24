def test_dashboard_stats(client, auth_headers):
    """Test statistiques du dashboard"""
    response = client.get("/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "total_stock" in data
    assert "total_entries" in data
    assert "total_exits" in data
    assert isinstance(data["total_products"], int)
    assert isinstance(data["total_stock"], int)

def test_dashboard_movements(client, auth_headers):
    """Test historique des mouvements du dashboard"""
    response = client.get("/dashboard/movements", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_dashboard_movement_stats(client, auth_headers):
    """Test statistiques par période"""
    response = client.get("/dashboard/movement-stats?period=day", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_dashboard_low_stock(client, auth_headers):
    """Test produits avec stock bas"""
    response = client.get("/dashboard/low-stock", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_dashboard_low_stock_with_threshold(client, auth_headers):
    """Test produits avec stock bas avec seuil personnalisé"""
    response = client.get("/dashboard/low-stock?threshold=10", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_dashboard_chart_data(client, auth_headers):
    """Test données pour graphique"""
    response = client.get("/dashboard/chart/movements", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "entries" in data
    assert "exits" in data
    assert isinstance(data["labels"], list)
    assert isinstance(data["entries"], list)
    assert isinstance(data["exits"], list)

def test_dashboard_notify_low_stock(client, auth_headers):
    """Test notification stock bas"""
    response = client.get("/dashboard/notify/low-stock", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "low_stock_products" in data
    assert isinstance(data["low_stock_products"], list)

def test_export_products_csv(client, auth_headers):
    """Test export CSV des produits"""
    response = client.get("/dashboard/export/products", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
    assert "attachment" in response.headers["content-disposition"]
    assert "filename=products.csv" in response.headers["content-disposition"]

def test_dashboard_movements_with_filters(client, auth_headers):
    """Test historique avec filtres"""
    response = client.get(
        "/dashboard/movements?start_date=2024-01-01&product_id=1",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_movement_stats_all_periods(client, auth_headers):
    """Test stats pour toutes les périodes"""
    for period in ["day", "week", "month"]:
        response = client.get(
            f"/dashboard/movement-stats?period={period}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
