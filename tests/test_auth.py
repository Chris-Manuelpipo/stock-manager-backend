def test_login_success(client):
    """Test de login réussi"""
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    """Test de login avec mauvais mot de passe"""
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401

def test_login_wrong_username(client):
    """Test de login avec mauvais username"""
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent", "password": "admin123"}
    )
    assert response.status_code == 401

def test_get_me_with_token(client, auth_headers):
    """Test de récupération du profil avec token valide"""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert "email" in data
    assert "role" in data

def test_get_me_without_token(client):
    """Test de récupération du profil sans token"""
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_get_me_with_invalid_token(client):
    """Test de récupération du profil avec token invalide"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 400

def test_refresh_token(client):
    """Test de rafraîchissement du token"""
    # D'abord login
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Rafraîchir
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_refresh_invalid_token(client):
    """Test de rafraîchissement avec token invalide"""
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "invalid_refresh_token"}
    )
    assert response.status_code == 400
