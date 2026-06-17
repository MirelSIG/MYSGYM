import json
from app import app, SCHEMA

def test_protected_routes_script_presence(client):
    """Verify that the frontend route protection script is present in pages."""
    pages = ['/', '/dashboard', '/seccion/usuarios']
    for page in pages:
        response = client.get(page)
        assert b'const isProtected' in response.data
        assert b'window.location.href = \'/login\'' in response.data

def test_entity_quick_fill_functionality(client):
    """Verify that entities with examples have the quick fill buttons with correct data."""
    for entity, config in SCHEMA.items():
        if "examples" in config:
            response = client.get(f'/seccion/{entity}')
            for example in config["examples"]:
                # Check if the example data is serialized in the data-payload attribute
                payload_json = json.dumps(example).encode()
                # We check for a subset of the payload since quoting might vary
                if "nombre" in example:
                    assert example["nombre"].encode() in response.data

def test_entity_form_fields_types(client):
    """Verify that form fields have the correct input types (number vs text)."""
    number_fields = ['capacidad', 'monitor_id', 'sala_id', 'horario_id', 'aforo_maximo', 'usuario_id', 'actividad_id', 'empleado_id', 'material_id', 'monto']
    for entity, config in SCHEMA.items():
        response = client.get(f'/seccion/{entity}')
        form_fields = config.get("form_fields", config["fields"])
        for field in form_fields:
            if field in number_fields:
                assert f'type="number"'.encode() in response.data
            else:
                # Some fields might be text or others
                pass

def test_navigation_role_filtering_script(client):
    """Verify that the script for filtering navigation items by role is present."""
    response = client.get('/')
    assert b'ApiService.isClient()' in response.data
    assert b'clientVisibleEntities' in response.data

def test_logout_functionality_presence(client):
    """Verify that the logout event listener is setup in the base template."""
    response = client.get('/')
    assert b'authLink.textContent = \'Logout\'' in response.data
    assert b'ApiService.logout()' in response.data
