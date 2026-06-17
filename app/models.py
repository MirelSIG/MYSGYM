from app import db
from datetime import datetime, timezone

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    estado = db.Column(db.String(20), default='activo')

    reservas = db.relationship('Reserva', backref='usuario', lazy=True)
    pagos = db.relationship('Pago', backref='usuario', lazy=True)

class Empleado(db.Model):
    __tablename__ = 'empleados'
    id_empleado = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) # Añadido para login
    fecha_contratacion = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())

    actividades = db.relationship('Actividad', backref='monitor', lazy=True)
    incidencias = db.relationship('Incidencia', backref='empleado', lazy=True)

class Sala(db.Model):
    __tablename__ = 'salas'
    id_sala = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    capacidad = db.Column(db.Integer)

    actividades = db.relationship('Actividad', backref='sala', lazy=True)
    materiales = db.relationship('Material', backref='sala', lazy=True)

class Horario(db.Model):
    __tablename__ = 'horarios'
    id_horario = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.String(20), nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

    actividades = db.relationship('Actividad', backref='horario', lazy=True)

class Actividad(db.Model):
    __tablename__ = 'actividades'
    id_actividad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    monitor_id = db.Column(db.Integer, db.ForeignKey('empleados.id_empleado'))
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id_sala'))
    horario_id = db.Column(db.Integer, db.ForeignKey('horarios.id_horario'))
    aforo_maximo = db.Column(db.Integer)

    reservas = db.relationship('Reserva', backref='actividad', lazy=True)

class Reserva(db.Model):
    __tablename__ = 'reservas'
    id_reserva = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividades.id_actividad'), nullable=False)
    fecha_reserva = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    estado = db.Column(db.String(20), default='pendiente')

class Pago(db.Model):
    __tablename__ = 'pagos'
    id_pago = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_pago = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column(db.String(50))
    estado = db.Column(db.String(20), default='Completado')

class Material(db.Model):
    __tablename__ = 'materiales'
    id_material = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50))
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id_sala'))

    incidencias = db.relationship('Incidencia', backref='material', lazy=True)

class Incidencia(db.Model):
    __tablename__ = 'incidencias'
    id_incidencia = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id_empleado'))
    material_id = db.Column(db.Integer, db.ForeignKey('materiales.id_material'))
    estado = db.Column(db.String(20), default='pendiente')
