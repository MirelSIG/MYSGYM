from flask import Blueprint, render_template

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route("/")
def home():
    # Datos mínimos para que el template no falle
    sections = [
        {
            "key": "usuarios",
            "title": "Usuarios",
            "accent": "Gestión de clientes",
            "description": "Información de usuarios registrados",
            "url": "/entity/usuarios"
        },
        {
            "key": "empleados",
            "title": "Empleados",
            "accent": "Personal del gimnasio",
            "description": "Entrenadores y personal administrativo",
            "url": "/entity/empleados"
        },
        {
            "key": "reservas",
            "title": "Reservas",
            "accent": "Gestión de reservas",
            "description": "Clases y actividades reservadas",
            "url": "/entity/reservas"
        },
        {
            "key": "pagos",
            "title": "Pagos",
            "accent": "Historial de pagos",
            "description": "Transacciones y facturación",
            "url": "/entity/pagos"
        }
    ]

    schema = {}  # Evita errores en home.html

    return render_template("home.html", sections=sections, schema=schema)


@frontend_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@frontend_bp.route("/entity/<name>")
def entity(name):
    return render_template("entity.html", entity=name)


@frontend_bp.route("/login")
def login():
    return render_template("login.html")
