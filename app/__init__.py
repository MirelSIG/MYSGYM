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
            r"http://127\.0\.0\.1:.*"
        ])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    with app.app_context():
        from . import models

    from app.routes.auth import auth_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.gym import gym_bp
    from app.routes.reservas import reservas_bp
    from app.routes.pagos import pagos_bp
    from app.routes.mantenimiento import mantenimiento_bp
    from app.routes.empleados import empleados_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(gym_bp, url_prefix='/api/gym')
    app.register_blueprint(reservas_bp, url_prefix='/api/reservas')
    app.register_blueprint(pagos_bp, url_prefix='/api/pagos')
    app.register_blueprint(mantenimiento_bp, url_prefix='/api/mantenimiento')
    app.register_blueprint(empleados_bp, url_prefix='/api/empleados')

    from app.routes.frontend_routes import frontend_bp
    app.register_blueprint(frontend_bp)

    @app.route('/api')
    def api_index():
        return {
            "status": "success",
            "message": "Bienvenido a la API de MYSGYM",
            "endpoints": {
                "auth": "/auth/register, /auth/login",
                "usuarios": "/usuarios (JWT)",
                "empleados": "/empleados (JWT)",
                "gym": "/gym/actividades, /gym/salas, /gym/horarios",
                "reservas": "/reservas (JWT)",
                "pagos": "/pagos (JWT)",
                "mantenimiento": "/mantenimiento/materiales, /mantenimiento/incidencias"
            }
        }

    return app


def seed_database(db):
    from app.models import Sala, Horario, Empleado, Usuario, Material
    from werkzeug.security import generate_password_hash
    from datetime import time

    if not Sala.query.get(1):
        db.session.add(Sala(id_sala=1, nombre="Sala de Yoga", capacidad=10))
    if not Sala.query.get(2):
        db.session.add(Sala(id_sala=2, nombre="Zona Musculación", capacidad=8))
    if not Sala.query.get(3):
        db.session.add(Sala(id_sala=3, nombre="Boxeo Pro", capacidad=5))
    if not Sala.query.get(4):
        db.session.add(Sala(id_sala=4, nombre="Sala de Pilates", capacidad=12))
    if not Sala.query.get(5):
        db.session.add(Sala(id_sala=5, nombre="Zona CrossFit", capacidad=15))

    if not Horario.query.get(1):
        db.session.add(Horario(id_horario=1, dia_semana="Lunes", hora_inicio=time(9, 0), hora_fin=time(10, 0)))
    if not Horario.query.get(2):
        db.session.add(Horario(id_horario=2, dia_semana="Martes", hora_inicio=time(10, 30), hora_fin=time(11, 30)))
    if not Horario.query.get(3):
        db.session.add(Horario(id_horario=3, dia_semana="Miercoles", hora_inicio=time(18, 30), hora_fin=time(19, 30)))
    if not Horario.query.get(4):
        db.session.add(Horario(id_horario=4, dia_semana="Jueves", hora_inicio=time(19, 0), hora_fin=time(20, 0)))
    if not Horario.query.get(5):
        db.session.add(Horario(id_horario=5, dia_semana="Viernes", hora_inicio=time(12, 0), hora_fin=time(13, 0)))

    if not Empleado.query.get(1):
        db.session.add(Empleado(id_empleado=1, nombre="Monitor Yoga", email="yoga@gym.com", rol="monitor", password_hash=generate_password_hash("1234")))
    if not Empleado.query.get(2):
        db.session.add(Empleado(id_empleado=2, nombre="Monitor Spinning", email="spinning@gym.com", rol="monitor", password_hash=generate_password_hash("1234")))
    if not Empleado.query.get(3):
        db.session.add(Empleado(id_empleado=3, nombre="Monitor Boxeo", email="boxeo@gym.com", rol="monitor", password_hash=generate_password_hash("1234")))
    if not Empleado.query.get(4):
        db.session.add(Empleado(id_empleado=4, nombre="Monitora Pilates", email="pilates@gym.com", rol="monitor", password_hash=generate_password_hash("1234")))
    if not Empleado.query.get(5):
        db.session.add(Empleado(id_empleado=5, nombre="Monitor CrossFit", email="crossfit@gym.com", rol="monitor", password_hash=generate_password_hash("1234")))

    if not Usuario.query.get(1):
        db.session.add(Usuario(id_usuario=1, nombre="Ana Garcia", email="ana@gym.com", password_hash=generate_password_hash("1234"), telefono="600123456"))
    if not Usuario.query.get(2):
        db.session.add(Usuario(id_usuario=2, nombre="Carlos Lopez", email="carlos@gym.com", password_hash=generate_password_hash("1234"), telefono="600123457"))
    if not Usuario.query.get(3):
        db.session.add(Usuario(id_usuario=3, nombre="Laura Martinez", email="laura@gym.com", password_hash=generate_password_hash("1234"), telefono="600123458"))
    if not Usuario.query.get(4):
        db.session.add(Usuario(id_usuario=4, nombre="David Fernandez", email="david@gym.com", password_hash=generate_password_hash("1234"), telefono="600123459"))
    if not Usuario.query.get(5):
        db.session.add(Usuario(id_usuario=5, nombre="Elena Gomez", email="elena@gym.com", password_hash=generate_password_hash("1234"), telefono="600123450"))

    if not Material.query.get(1):
        db.session.add(Material(id_material=1, nombre="Mancuernas 5kg", estado="bueno", sala_id=1))
    if not Material.query.get(2):
        db.session.add(Material(id_material=2, nombre="Bicicleta Estatica", estado="bueno", sala_id=2))
    if not Material.query.get(3):
        db.session.add(Material(id_material=3, nombre="Saco de Boxeo", estado="bueno", sala_id=3))
    if not Material.query.get(4):
        db.session.add(Material(id_material=4, nombre="Esterilla Pilates", estado="nuevo", sala_id=4))
    if not Material.query.get(5):
        db.session.add(Material(id_material=5, nombre="Kettlebell 16kg", estado="desgastado", sala_id=5))

    db.session.commit()