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
        from . import models  # noqa: F401 — registers models with SQLAlchemy

    # API blueprints
    from app.routes.auth import auth_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.gym import gym_bp
    from app.routes.reservas import reservas_bp
    from app.routes.pagos import pagos_bp
    from app.routes.mantenimiento import mantenimiento_bp
    from app.routes.empleados import empleados_bp

    app.register_blueprint(auth_bp,          url_prefix="/api/auth")
    app.register_blueprint(usuarios_bp,      url_prefix="/api/usuarios")
    app.register_blueprint(gym_bp,           url_prefix="/api/gym")
    app.register_blueprint(reservas_bp,      url_prefix="/api/reservas")
    app.register_blueprint(pagos_bp,         url_prefix="/api/pagos")
    app.register_blueprint(mantenimiento_bp, url_prefix="/api/mantenimiento")
    app.register_blueprint(empleados_bp,     url_prefix="/api/empleados")

    # Frontend blueprint
    from app.routes.frontend_routes import frontend_bp
    app.register_blueprint(frontend_bp)

    @app.route("/api")
    def api_index():
        return {
            "status": "success",
            "message": "Bienvenido a la API de MYSGYM",
            "endpoints": {
                "auth":           "/api/auth/register, /api/auth/login",
                "usuarios":       "/api/usuarios (JWT)",
                "empleados":      "/api/empleados (JWT)",
                "gym":            "/api/gym/actividades, /api/gym/salas, /api/gym/horarios",
                "reservas":       "/api/reservas (JWT)",
                "pagos":          "/api/pagos (JWT)",
                "mantenimiento":  "/api/mantenimiento/materiales, /api/mantenimiento/incidencias",
            },
        }

    return app


def seed_database(db):
    """Insert demo data if tables are empty."""
    from app.models import Sala, Horario, Empleado, Usuario, Material
    from werkzeug.security import generate_password_hash
    from datetime import time

    # Salas
    if not db.session.get(Sala, 1):
        db.session.add(Sala(id_sala=1, nombre="Sala de Yoga",      capacidad=10))
    if not db.session.get(Sala, 2):
        db.session.add(Sala(id_sala=2, nombre="Zona Musculación",  capacidad=8))
    if not db.session.get(Sala, 3):
        db.session.add(Sala(id_sala=3, nombre="Boxeo Pro",         capacidad=5))
    if not db.session.get(Sala, 4):
        db.session.add(Sala(id_sala=4, nombre="Sala de Pilates",   capacidad=10))
    if not db.session.get(Sala, 5):
        db.session.add(Sala(id_sala=5, nombre="Zona CrossFit",     capacidad=10))

    # Horarios
    if not db.session.get(Horario, 1):
        db.session.add(Horario(id_horario=1, dia_semana="Lunes",     hora_inicio=time(9,  0), hora_fin=time(10, 0)))
    if not db.session.get(Horario, 2):
        db.session.add(Horario(id_horario=2, dia_semana="Martes",    hora_inicio=time(10,30), hora_fin=time(11,30)))
    if not db.session.get(Horario, 3):
        db.session.add(Horario(id_horario=3, dia_semana="Miercoles", hora_inicio=time(18,30), hora_fin=time(19,30)))
    if not db.session.get(Horario, 4):
        db.session.add(Horario(id_horario=4, dia_semana="Jueves",    hora_inicio=time(19, 0), hora_fin=time(20, 0)))
    if not db.session.get(Horario, 5):
        db.session.add(Horario(id_horario=5, dia_semana="Viernes",   hora_inicio=time(12, 0), hora_fin=time(13, 0)))

    # Empleados
    _pw = generate_password_hash("1234")
    if not db.session.get(Empleado, 1):
        db.session.add(Empleado(id_empleado=1, nombre="Monitor Yoga",     email="yoga@gym.com",     rol="monitor", password_hash=_pw))
    if not db.session.get(Empleado, 2):
        db.session.add(Empleado(id_empleado=2, nombre="Monitor Spinning",  email="spinning@gym.com", rol="monitor", password_hash=_pw))
    if not db.session.get(Empleado, 3):
        db.session.add(Empleado(id_empleado=3, nombre="Monitor Boxeo",    email="boxeo@gym.com",    rol="monitor", password_hash=_pw))
    if not db.session.get(Empleado, 4):
        db.session.add(Empleado(id_empleado=4, nombre="Monitora Pilates", email="pilates@gym.com",  rol="monitor", password_hash=_pw))
    if not db.session.get(Empleado, 5):
        db.session.add(Empleado(id_empleado=5, nombre="Monitor CrossFit", email="crossfit@gym.com", rol="monitor", password_hash=_pw))
    # Admin account
    if not Empleado.query.filter_by(email="admin@mysgym.com").first():
        db.session.add(Empleado(nombre="Administrador", email="admin@mysgym.com", rol="admin",
                                password_hash=generate_password_hash("admin123")))

    # Usuarios
    _pw_u = generate_password_hash("1234")
    if not db.session.get(Usuario, 1):
        db.session.add(Usuario(id_usuario=1, nombre="Ana Garcia",      email="ana@gym.com",    password_hash=_pw_u, telefono="600123456"))
    if not db.session.get(Usuario, 2):
        db.session.add(Usuario(id_usuario=2, nombre="Carlos Lopez",    email="carlos@gym.com", password_hash=_pw_u, telefono="600123457"))
    if not db.session.get(Usuario, 3):
        db.session.add(Usuario(id_usuario=3, nombre="Laura Martinez",  email="laura@gym.com",  password_hash=_pw_u, telefono="600123458"))
    if not db.session.get(Usuario, 4):
        db.session.add(Usuario(id_usuario=4, nombre="David Fernandez", email="david@gym.com",  password_hash=_pw_u, telefono="600123459"))
    if not db.session.get(Usuario, 5):
        db.session.add(Usuario(id_usuario=5, nombre="Elena Gomez",     email="elena@gym.com",  password_hash=_pw_u, telefono="600123450"))
    # Demo cliente account
    if not Usuario.query.filter_by(email="cliente@mysgym.com").first():
        db.session.add(Usuario(nombre="Cliente Demo", email="cliente@mysgym.com",
                               password_hash=generate_password_hash("cliente123"), telefono="600000000"))

    # Materiales
    if not db.session.get(Material, 1):
        db.session.add(Material(id_material=1, nombre="Mancuernas 5kg",    estado="bueno",     sala_id=1))
    if not db.session.get(Material, 2):
        db.session.add(Material(id_material=2, nombre="Bicicleta Estatica", estado="bueno",    sala_id=2))
    if not db.session.get(Material, 3):
        db.session.add(Material(id_material=3, nombre="Saco de Boxeo",     estado="bueno",     sala_id=3))
    if not db.session.get(Material, 4):
        db.session.add(Material(id_material=4, nombre="Esterilla Pilates", estado="nuevo",     sala_id=4))
    if not db.session.get(Material, 5):
        db.session.add(Material(id_material=5, nombre="Kettlebell 16kg",   estado="desgastado",sala_id=5))

    db.session.commit()
