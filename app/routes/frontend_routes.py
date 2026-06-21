from flask import Blueprint, render_template, redirect, url_for

frontend_bp = Blueprint("frontend", __name__)

# ──────────────────────────────────────────────
# Schema central — define cada entidad visible
# ──────────────────────────────────────────────
ENTITY_SCHEMA = {
    "usuarios": {
        "title": "Usuarios",
        "accent": "Gestión de clientes",
        "description": "Información de usuarios registrados en el gimnasio.",
        "id_field": "id_usuario",
        "fields": ["nombre", "email", "telefono", "estado", "fecha_registro"],
        "form_fields": ["nombre", "email", "telefono", "estado"],
        "api_url": "/api/usuarios/",
        "examples": [
            {"nombre": "Ana García", "email": "ana@gym.com", "telefono": "600111222", "estado": "activo"},
            {"nombre": "Carlos López", "email": "carlos@gym.com", "telefono": "600333444", "estado": "activo"},
        ],
    },
    "empleados": {
        "title": "Empleados",
        "accent": "Personal del gimnasio",
        "description": "Entrenadores y personal administrativo.",
        "id_field": "id_empleado",
        "fields": ["nombre", "email", "rol", "fecha_contratacion"],
        "form_fields": ["nombre", "email", "rol"],
        "api_url": "/api/empleados/",
        "examples": [
            {"nombre": "Monitor Yoga", "email": "yoga@gym.com", "rol": "monitor"},
            {"nombre": "Admin General", "email": "admin@gym.com", "rol": "admin"},
        ],
    },
    "salas": {
        "title": "Salas",
        "accent": "Espacios del gimnasio",
        "description": "Salas disponibles para actividades y clases.",
        "id_field": "id_sala",
        "fields": ["nombre", "capacidad"],
        "form_fields": ["nombre", "capacidad"],
        "api_url": "/api/gym/salas",
        "examples": [
            {"nombre": "Sala Yoga", "capacidad": 10},
            {"nombre": "Zona Crossfit", "capacidad": 8},
        ],
    },
    "horarios": {
        "title": "Horarios",
        "accent": "Franjas horarias",
        "description": "Días y horas en que se imparten las actividades.",
        "id_field": "id_horario",
        "fields": ["dia_semana", "hora_inicio", "hora_fin"],
        "form_fields": ["dia_semana", "hora_inicio", "hora_fin"],
        "api_url": "/api/gym/horarios",
        "examples": [
            {"dia_semana": "Lunes", "hora_inicio": "09:00", "hora_fin": "10:00"},
            {"dia_semana": "Miercoles", "hora_inicio": "18:30", "hora_fin": "19:30"},
        ],
    },
    "actividades": {
        "title": "Actividades",
        "accent": "Clases del gimnasio",
        "description": "Actividades impartidas por monitores en las salas.",
        "id_field": "id_actividad",
        "fields": ["nombre", "descripcion", "monitor_id", "sala_id", "horario_id", "aforo_maximo"],
        "form_fields": ["nombre", "descripcion", "monitor_id", "sala_id", "horario_id", "aforo_maximo"],
        "api_url": "/api/gym/actividades",
        "examples": [
            {"nombre": "Yoga Matutino", "descripcion": "Clase de yoga para principiantes", "monitor_id": 1, "sala_id": 1, "horario_id": 1, "aforo_maximo": 8},
            {"nombre": "Boxeo Avanzado", "descripcion": "Técnica y sparring", "monitor_id": 3, "sala_id": 3, "horario_id": 3, "aforo_maximo": 5},
        ],
    },
    "reservas": {
        "title": "Reservas",
        "accent": "Gestión de reservas",
        "description": "Clases y actividades reservadas por los socios.",
        "id_field": "id_reserva",
        "fields": ["usuario_id", "actividad_id", "estado"],
        "form_fields": ["usuario_id", "actividad_id"],
        "api_url": "/api/reservas",
        "examples": [
            {"usuario_id": 1, "actividad_id": 1},
            {"usuario_id": 2, "actividad_id": 2},
        ],
    },
    "pagos": {
        "title": "Pagos",
        "accent": "Historial de pagos",
        "description": "Transacciones y facturación de los socios.",
        "id_field": "id_pago",
        "fields": ["usuario_id", "monto", "metodo_pago", "estado", "fecha_pago"],
        "form_fields": ["usuario_id", "monto", "metodo_pago"],
        "api_url": "/api/pagos",
        "examples": [
            {"usuario_id": 1, "monto": 30.00, "metodo_pago": "Tarjeta"},
            {"usuario_id": 2, "monto": 50.00, "metodo_pago": "Efectivo"},
        ],
    },
    "materiales": {
        "title": "Materiales",
        "accent": "Inventario del gimnasio",
        "description": "Equipamiento disponible en cada sala.",
        "id_field": "id_material",
        "fields": ["nombre", "estado", "sala_id"],
        "form_fields": ["nombre", "estado", "sala_id"],
        "api_url": "/api/mantenimiento/materiales",
        "examples": [
            {"nombre": "Mancuernas 5kg", "estado": "bueno", "sala_id": 1},
            {"nombre": "Saco de Boxeo", "estado": "desgastado", "sala_id": 3},
        ],
    },
    "incidencias": {
        "title": "Incidencias",
        "accent": "Mantenimiento",
        "description": "Incidencias reportadas sobre el material del gimnasio.",
        "id_field": "id_incidencia",
        "fields": ["descripcion", "material_id", "empleado_id", "estado", "fecha"],
        "form_fields": ["descripcion", "material_id", "empleado_id"],
        "api_url": "/api/mantenimiento/incidencias",
        "examples": [
            {"descripcion": "Bicicleta estática con ruido", "material_id": 2, "empleado_id": 1},
            {"descripcion": "Saco de boxeo roto", "material_id": 3, "empleado_id": 3},
        ],
    },
}

NAV_ITEMS = [
    {"key": "salas",       "title": "Salas",       "url": "/entity/salas"},
    {"key": "horarios",    "title": "Horarios",    "url": "/entity/horarios"},
    {"key": "actividades", "title": "Actividades", "url": "/entity/actividades"},
    {"key": "reservas",    "title": "Reservas",    "url": "/entity/reservas"},
    {"key": "pagos",       "title": "Pagos",       "url": "/entity/pagos"},
    {"key": "materiales",  "title": "Materiales",  "url": "/entity/materiales"},
    {"key": "incidencias", "title": "Incidencias", "url": "/entity/incidencias"},
]

HOME_SECTIONS = [
    {
        "key": "usuarios",
        "title": "Usuarios",
        "accent": "Gestión de clientes",
        "description": "Información de usuarios registrados en el gimnasio.",
        "url": "/entity/usuarios",
    },
    {
        "key": "empleados",
        "title": "Empleados",
        "accent": "Personal del gimnasio",
        "description": "Entrenadores y personal administrativo.",
        "url": "/entity/empleados",
    },
    {
        "key": "actividades",
        "title": "Actividades",
        "accent": "Clases del gimnasio",
        "description": "Actividades impartidas por monitores en las salas.",
        "url": "/entity/actividades",
    },
    {
        "key": "reservas",
        "title": "Reservas",
        "accent": "Gestión de reservas",
        "description": "Clases y actividades reservadas por los socios.",
        "url": "/entity/reservas",
    },
    {
        "key": "pagos",
        "title": "Pagos",
        "accent": "Historial de pagos",
        "description": "Transacciones y facturación de los socios.",
        "url": "/entity/pagos",
    },
    {
        "key": "materiales",
        "title": "Materiales",
        "accent": "Inventario del gimnasio",
        "description": "Equipamiento disponible en cada sala.",
        "url": "/entity/materiales",
    },
    {
        "key": "incidencias",
        "title": "Incidencias",
        "accent": "Mantenimiento",
        "description": "Incidencias reportadas sobre el material.",
        "url": "/entity/incidencias",
    },
]


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@frontend_bp.route("/")
def home():
    return render_template(
        "home.html",
        sections=HOME_SECTIONS,
        schema={},
        nav_items=NAV_ITEMS,
        active_page="home",
    )


@frontend_bp.route("/dashboard")
def dashboard():
    return render_template(
        "dashboard.html",
        nav_items=NAV_ITEMS,
        active_page="dashboard",
    )


@frontend_bp.route("/entity/<name>")
def entity(name):
    config = ENTITY_SCHEMA.get(name)
    if not config:
        return redirect(url_for("frontend.home"))
    return render_template(
        "entity.html",
        entity=name,
        config=config,
        nav_items=NAV_ITEMS,
        active_page=name,
    )


@frontend_bp.route("/login")
def login():
    return render_template("login.html", nav_items=NAV_ITEMS, active_page="login")


@frontend_bp.route("/register")
def register():
    return render_template("register.html", nav_items=NAV_ITEMS, active_page="register")
