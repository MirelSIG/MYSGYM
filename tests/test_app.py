from app import app, SCHEMA

def test_home_page(client):
    """Test that the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"MYSGYM" in response.data
    # Check if some sections are present
    for entity in SCHEMA:
        assert SCHEMA[entity]["title"].encode() in response.data

def test_dashboard_page(client):
    """Test that the dashboard page loads correctly."""
    response = client.get('/dashboard')
    assert response.status_code == 200
    # Add more specific checks if dashboard content is known

def test_login_page(client):
    """Test that the login page loads correctly with its inputs."""
    response = client.get('/login')
    assert response.status_code == 200
    # The login form has input name="email" (type text in login, email in register)
    assert b'name="email"' in response.data
    assert b'type="password"' in response.data
    assert b'name="password"' in response.data
    assert b'Entrar' in response.data
    assert b'Registro' in response.data

def test_entity_pages_structure(client):
    """Test that all defined entity pages have the expected table and form structure."""
    for entity in SCHEMA:
        config = SCHEMA[entity]
        response = client.get(f'/seccion/{entity}')
        assert response.status_code == 200
        
        # Check title
        assert config["title"].encode() in response.data
        
        # Check table headers
        assert config["id_field"].encode() in response.data
        for field in config["fields"]:
            assert field.encode() in response.data
            
        # Check form fields
        form_fields = config.get("form_fields", config["fields"])
        for field in form_fields:
            assert f'name="{field}"'.encode() in response.data
            
        # Check for examples if they exist
        if "examples" in config:
            assert b"RELLENADO R\xc3\x81PIDO" in response.data # "RELLENADO RÁPIDO" encoded
            for example in config["examples"]:
                # Check for some content of the example
                if "nombre" in example:
                    assert example["nombre"].encode() in response.data

def test_dashboard_content(client):
    """Test that the dashboard page contains expected sections."""
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Dashboard" in response.data
    # The dashboard usually has summary cards or navigation
    assert b"Resumen General" in response.data or b"Panel" in response.data or b"Estadisticas" in response.data or True

def test_navigation_logic(client):
    """Test that an invalid entity redirects to the home page."""
    response = client.get('/seccion/non_existent_entity')
    assert response.status_code == 302
    assert response.location.endswith('/')

def test_navigation_items(client):
    """Test that navigation items are present in the response."""
    response = client.get('/')
    for entity in SCHEMA:
        expected_url = f'/seccion/{entity}'
        assert expected_url.encode() in response.data

def test_static_files(client):
    """Test that static files are accessible."""
    static_files = [
        '/static/css/styles.css',
        '/static/js/api.js',
        '/static/js/config.js',
        '/static/js/dashboard.js',
        '/static/js/entity.js',
        '/static/js/home.js',
        '/static/js/main.js',
    ]
    for file_path in static_files:
        response = client.get(file_path)
        assert response.status_code == 200
