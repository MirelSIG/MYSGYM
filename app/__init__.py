import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_class)

    frontend_origin = os.environ.get("FRONTEND_ORIGIN", "").strip()
    if frontend_origin:
        CORS(app, origins=[frontend_origin])
    else:
        CORS(app, origins=[
            r"https://.*\.onrender\.com",
            r"http://localhost:.*",
            r"http://127\.0\.0\.1:.*",
        ])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    with app.app_context():
        from . import models  # noqa: F401 — registra modelos en SQLAlchemy

    # ── API Blueprints ────────────────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.gym import gym_bp
    from app.routes.reservas import reservas_bp
    from app.routes.pagos import pagos_bp
    from app.routes.mantenimiento import mantenimiento_bp
    from app.routes.empleados import empleados_bp

    app.register_blueprint(auth_bp,          url_prefix='/api/auth')
    app.register_blueprint(usuarios_bp,      url_prefix='/api/usuarios')
    app.register_blueprint(gym_bp,           url_prefix='/api/gym')
    app.register_blueprint(reservas_bp,      url_prefix='/api/reservas')
    app.register_blueprint(pagos_bp,         url_prefix='/api/pagos')
    app.register_blueprint(mantenimiento_bp, url_prefix='/api/mantenimiento')
    app.register_blueprint(empleados_bp,     url_prefix='/api/empleados')

    # ── Frontend Blueprint ────────────────────────────────────────────────────
    from app.routes.frontend_routes import frontend_bp
    app.register_blueprint(frontend_bp)

    @app.route('/api')
    def api_index():
        return {
            "status": "success",
            "message": "Bienvenido a la API de MYSGYM",
            "endpoints": {
                "auth":           "/api/auth/register, /api/auth/login",
                "usuarios":       "/api/usuarios/ (JWT)",
                "empleados":      "/api/empleados/ (JWT)",
                "gym":            "/api/gym/actividades, /api/gym/salas, /api/gym/horarios",
                "reservas":       "/api/reservas (JWT)",
                "pagos":          "/api/pagos (JWT)",
                "mantenimiento":  "/api/mantenimiento/materiales, /api/mantenimiento/incidencias",
            },
        }

    return app


def seed_database(db):
    """Inserta datos de ejemplo solo si las tablas están vacías."""
    from app.models import Sala, Horario, Empleado, Usuario, Material
    from werkzeug.security import generate_password_hash
    from datetime import time

    # Salas
    if not Sala.query.first():
        db.session.add_all([
            Sala(id_sala=1, nombre="Sala de Yoga",       capacidad=10),
            Sala(id_sala=2, nombre="Zona Musculación",   capacidad=8),
            Sala(id_sala=3, nombre="Boxeo Pro",          capacidad=5),
            Sala(id_sala=4, nombre="Sala de Pilates",    capacidad=8),
            Sala(id_sala=5, nombre="Zona CrossFit",      capacidad=6),
        ])

    # Horarios
    if not Horario.query.first():
        db.session.add_all([
            Horario(id_horario=1, dia_semana="Lunes",     hora_inicio=time(9, 0),  hora_fin=time(10, 0)),
            Horario(id_horario=2, dia_semana="Martes",    hora_inicio=time(10, 30),hora_fin=time(11, 30)),
            Horario(id_horario=3, dia_semana="Miércoles", hora_inicio=time(18, 30),hora_fin=time(19, 30)),
            Horario(id_horario=4, dia_semana="Jueves",    hora_inicio=time(19, 0), hora_fin=time(20, 0)),
            Horario(id_horario=5, dia_semana="Viernes",   hora_inicio=time(12, 0), hora_fin=time(13, 0)),
        ])

    # Empleados
    if not Empleado.query.first():
        db.session.add_all([
            Empleado(id_empleado=1, nombre="Monitor Yoga",     email="yoga@gym.com",     rol="monitor", password_hash=generate_password_hash("1234")),
            Empleado(id_empleado=2, nombre="Monitor Spinning", email="spinning@gym.com", rol="monitor", password_hash=generate_password_hash("1234")),
            Empleado(id_empleado=3, nombre="Monitor Boxeo",    email="boxeo@gym.com",    rol="monitor", password_hash=generate_password_hash("1234")),
            Empleado(id_empleado=4, nombre="Monitora Pilates", email="pilates@gym.com",  rol="monitor", password_hash=generate_password_hash("1234")),
            Empleado(id_empleado=5, nombre="Monitor CrossFit", email="crossfit@gym.com", rol="monitor", password_hash=generate_password_hash("1234")),
            Empleado(id_empleado=6, nombre="Admin MYSGYM",     email="admin@mysgym.com", rol="admin",   password_hash=generate_password_hash("admin123")),
        ])

    # Usuarios
    if not Usuario.query.first():
        db.session.add_all([
            Usuario(id_usuario=1, nombre="Ana García",       email="ana@gym.com",    password_hash=generate_password_hash("1234"), telefono="600123456"),
            Usuario(id_usuario=2, nombre="Carlos López",     email="carlos@gym.com", password_hash=generate_password_hash("1234"), telefono="600123457"),
            Usuario(id_usuario=3, nombre="Laura Martínez",   email="laura@gym.com",  password_hash=generate_password_hash("1234"), telefono="600123458"),
            Usuario(id_usuario=4, nombre="David Fernández",  email="david@gym.com",  password_hash=generate_password_hash("1234"), telefono="600123459"),
            Usuario(id_usuario=5, nombre="Elena Gómez",      email="elena@gym.com",  password_hash=generate_password_hash("1234"), telefono="600123450"),
            # Usuario demo para login
            Usuario(id_usuario=6, nombre="Cliente Demo",     email="cliente@mysgym.com", password_hash=generate_password_hash("cliente123"), telefono="600000001"),
        ])

    # Material
    if not Material.query.first():
        db.session.add_all([
            Material(id_material=1, nombre="Mancuernas 5kg",    estado="bueno",      sala_id=1),
            Material(id_material=2, nombre="Bicicleta Estática",estado="bueno",      sala_id=2),
            Material(id_material=3, nombre="Saco de Boxeo",     estado="bueno",      sala_id=3),
            Material(id_material=4, nombre="Esterilla Pilates", estado="nuevo",      sala_id=4),
            Material(id_material=5, nombre="Kettlebell 16kg",   estado="desgastado", sala_id=5),
        ])

    db.session.commit()
