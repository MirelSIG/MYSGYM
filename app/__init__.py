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
    """
    Insert demo data only when each row is missing.
    Fully idempotent: safe to call on every boot.
    Uses email/nombre uniqueness checks — never hard-codes PKs —
    to avoid duplicate-key violations on PostgreSQL sequences.
    """
    from app.models import Sala, Horario, Empleado, Usuario, Material
    from werkzeug.security import generate_password_hash
    from datetime import time
    import sqlalchemy.exc

    def _add(obj):
        """Add obj to session and flush immediately so constraint errors surface
        one row at a time; roll back only that row on collision."""
        try:
            db.session.add(obj)
            db.session.flush()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()

    # ── Salas ────────────────────────────────────────────────────────────────
    _salas = [
        ("Sala de Yoga",    10),
        ("Zona Musculación", 8),
        ("Boxeo Pro",        5),
        ("Sala de Pilates", 10),
        ("Zona CrossFit",   10),
    ]
    for nombre, cap in _salas:
        if not Sala.query.filter_by(nombre=nombre).first():
            _add(Sala(nombre=nombre, capacidad=cap))

    # ── Horarios ─────────────────────────────────────────────────────────────
    _horarios = [
        ("Lunes",     time(9,  0), time(10, 0)),
        ("Martes",    time(10,30), time(11,30)),
        ("Miercoles", time(18,30), time(19,30)),
        ("Jueves",    time(19, 0), time(20, 0)),
        ("Viernes",   time(12, 0), time(13, 0)),
    ]
    for dia, inicio, fin in _horarios:
        if not Horario.query.filter_by(dia_semana=dia, hora_inicio=inicio).first():
            _add(Horario(dia_semana=dia, hora_inicio=inicio, hora_fin=fin))

    # Flush salas/horarios so their auto-generated IDs are available for FK refs
    try:
        db.session.flush()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()

    # ── Empleados ────────────────────────────────────────────────────────────
    _pw = generate_password_hash("1234")
    _empleados = [
        ("Monitor Yoga",     "yoga@gym.com",     "monitor"),
        ("Monitor Spinning", "spinning@gym.com", "monitor"),
        ("Monitor Boxeo",    "boxeo@gym.com",    "monitor"),
        ("Monitora Pilates", "pilates@gym.com",  "monitor"),
        ("Monitor CrossFit", "crossfit@gym.com", "monitor"),
        ("Administrador",    "admin@mysgym.com", "admin"),
    ]
    for nombre, email, rol in _empleados:
        if not Empleado.query.filter_by(email=email).first():
            _add(Empleado(nombre=nombre, email=email, rol=rol, password_hash=_pw))

    # ── Usuarios ─────────────────────────────────────────────────────────────
    _pw_u = generate_password_hash("1234")
    _usuarios = [
        ("Ana Garcia",      "ana@gym.com",       "600123456"),
        ("Carlos Lopez",    "carlos@gym.com",    "600123457"),
        ("Laura Martinez",  "laura@gym.com",     "600123458"),
        ("David Fernandez", "david@gym.com",     "600123459"),
        ("Elena Gomez",     "elena@gym.com",     "600123450"),
        ("Cliente Demo",    "cliente@mysgym.com","600000000"),
    ]
    for nombre, email, tel in _usuarios:
        if not Usuario.query.filter_by(email=email).first():
            _add(Usuario(nombre=nombre, email=email,
                         password_hash=generate_password_hash("cliente123") if "mysgym" in email else _pw_u,
                         telefono=tel))

    # Flush so sala IDs exist before material FK refs
    try:
        db.session.flush()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()

    # ── Materiales ───────────────────────────────────────────────────────────
    # Resolve sala IDs dynamically instead of assuming 1-5
    sala_map = {s.nombre: s.id_sala for s in Sala.query.all()}
    _materiales = [
        ("Mancuernas 5kg",     "bueno",      "Sala de Yoga"),
        ("Bicicleta Estatica", "bueno",      "Zona Musculación"),
        ("Saco de Boxeo",      "bueno",      "Boxeo Pro"),
        ("Esterilla Pilates",  "nuevo",      "Sala de Pilates"),
        ("Kettlebell 16kg",    "desgastado", "Zona CrossFit"),
    ]
    for nombre, estado, sala_nombre in _materiales:
        if not Material.query.filter_by(nombre=nombre).first():
            _add(Material(nombre=nombre, estado=estado,
                          sala_id=sala_map.get(sala_nombre)))

    # ── Final commit ─────────────────────────────────────────────────────────
    try:
        db.session.commit()
        print("[seed] Demo data seeded successfully.")
    except sqlalchemy.exc.IntegrityError as exc:
        db.session.rollback()
        print(f"[seed] Seed skipped (data already present): {exc.orig}")
