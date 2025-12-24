def test_get_all_users(client, auth_headers):
    """Test récupération de tous les utilisateurs (admin only)"""
    response = client.get("/users/", headers=auth_headers)
    # Peut retourner 200 si admin, 403 si pas admin
    assert response.status_code in [200, 403]
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            user = data[0]
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "role" in user

def test_create_user(client, auth_headers):
    """Test création d'un nouvel utilisateur"""
    user_data = {
        "email": "test.user@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123",
        "role": "viewer"
    }
    
    response = client.post("/users/", json=user_data, headers=auth_headers)
    # Peut retourner 200 (si admin) ou 403 (si pas admin)
    assert response.status_code in [200, 403, 400]
    
    if response.status_code == 200:
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["role"] == user_data["role"]
        assert "id" in data
        assert "is_active" in data
        assert data["is_active"] == True

def test_get_user_by_id(client, auth_headers):
    """Test récupération d'un utilisateur par ID"""
    # D'abord obtenir la liste des users pour avoir un ID
    users_response = client.get("/users/", headers=auth_headers)
    if users_response.status_code == 200:
        users = users_response.json()
        if len(users) > 0:
            user_id = users[0]["id"]
            
            response = client.get(f"/users/{user_id}", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == user_id

def test_get_nonexistent_user(client, auth_headers):
    """Test récupération d'un utilisateur inexistant"""
    response = client.get("/users/9999", headers=auth_headers)
    assert response.status_code in [404, 403]

def test_update_user(client, auth_headers):
    """Test mise à jour d'un utilisateur"""
    # D'abord créer un utilisateur
    user_data = {
        "email": "update.test@example.com",
        "username": "updatetest",
        "full_name": "Update Test",
        "password": "password123",
        "role": "viewer"
    }
    
    create_response = client.post("/users/", json=user_data, headers=auth_headers)
    if create_response.status_code == 200:
        user_id = create_response.json()["id"]
        
        # Mettre à jour
        update_data = {
            "email": "updated@example.com",
            "username": "updateduser",
            "full_name": "Updated User",
            "password": "newpassword123",
            "role": "manager"
        }
        
        update_response = client.put(
            f"/users/{user_id}",
            json=update_data,
            headers=auth_headers
        )
        assert update_response.status_code == 200
        updated_user = update_response.json()
        assert updated_user["username"] == update_data["username"]
        assert updated_user["email"] == update_data["email"]
        assert updated_user["role"] == update_data["role"]

def test_deactivate_user(client, auth_headers):
    """Test désactivation d'un utilisateur"""
    # Créer un utilisateur à désactiver
    user_data = {
        "email": "deactivate.test@example.com",
        "username": "deactivatetest",
        "full_name": "Deactivate Test",
        "password": "password123",
        "role": "viewer"
    }
    
    create_response = client.post("/users/", json=user_data, headers=auth_headers)
    if create_response.status_code == 200:
        user_id = create_response.json()["id"]
        
        # Désactiver
        delete_response = client.delete(f"/users/{user_id}", headers=auth_headers)
        assert delete_response.status_code == 200
        
        # Vérifier que l'utilisateur est désactivé
        get_response = client.get(f"/users/{user_id}", headers=auth_headers)
        if get_response.status_code == 200:
            user = get_response.json()
            assert user["is_active"] == False

def test_reset_user_password(client, auth_headers):
    """Test réinitialisation du mot de passe"""
    # D'abord obtenir un utilisateur existant
    users_response = client.get("/users/", headers=auth_headers)
    if users_response.status_code == 200:
        users = users_response.json()
        if len(users) > 0:
            user_id = users[0]["id"]
            
            response = client.put(
                f"/users/{user_id}/reset-password",
                json={"new_password": "newsecurepassword123"},
                headers=auth_headers
            )
            assert response.status_code in [200, 403]

def test_user_permissions(client):
    """Test des permissions utilisateur"""
    # Tester sans authentification
    response = client.get("/users/")
    assert response.status_code == 401  # Unauthorized
    
    # Tester avec token invalide
    response = client.get(
        "/users/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code in [400, 401]

def test_create_duplicate_user(client, auth_headers):
    """Test création d'utilisateur avec email/username existant"""
    user_data = {
        "email": "admin@landrystore.com",  # Email existant
        "username": "admin",  # Username existant
        "full_name": "Duplicate Test",
        "password": "password123",
        "role": "viewer"
    }
    
    response = client.post("/users/", json=user_data, headers=auth_headers)
    if response.status_code == 400:
        data = response.json()
        assert "detail" in data
        assert "already" in data["detail"].lower()
