from flask import Blueprint, jsonify, request
from app.models import Actividad, Sala, Horario, db
from flask_jwt_extended import jwt_required
from app.utils import admin_required

gym_bp = Blueprint('gym', __name__)

# --- ENDPOINTS PARA ACTIVIDADES ---

@gym_bp.route('/actividades', methods=['GET'])
def get_actividades():
    actividades = Actividad.query.all()
    return jsonify([{
        "id_actividad": a.id_actividad,
        "nombre": a.nombre,
        "descripcion": a.descripcion,
        "aforo_maximo": a.aforo_maximo,
        "sala": a.sala.nombre if a.sala else None,
        "sala_id": a.sala_id,
        "monitor": a.monitor.nombre if a.monitor else None,
        "monitor_id": a.monitor_id,
        "horario": f"{a.horario.dia_semana} {a.horario.hora_inicio}-{a.horario.hora_fin}" if a.horario else None,
        "horario_id": a.horario_id
    } for a in actividades]), 200

@gym_bp.route('/actividades', methods=['POST'])
@jwt_required()
@admin_required()
def create_actividad():
    data = request.get_json()
    sala_id = data.get('sala_id')
    aforo_maximo = data.get('aforo_maximo')

    if sala_id and aforo_maximo:
        sala = db.session.get(Sala, sala_id)
        if sala and aforo_maximo > sala.capacidad:
            return jsonify({"message": f"El aforo máximo ({aforo_maximo}) no puede superar la capacidad de la sala ({sala.capacidad})"}), 400

    nueva_actividad = Actividad(
        nombre=data.get('nombre'),
        descripcion=data.get('descripcion'),
        monitor_id=data.get('monitor_id'),
        sala_id=sala_id,
        horario_id=data.get('horario_id'),
        aforo_maximo=aforo_maximo
    )
    db.session.add(nueva_actividad)
    db.session.commit()
    return jsonify({"message": "Actividad creada con éxito"}), 201

@gym_bp.route('/actividades/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_actividad(id):
    actividad = db.session.get(Actividad, id)
    if not actividad:
        return jsonify({"message": "Actividad no encontrada"}), 404
    data = request.get_json()

    nuevo_sala_id = data.get('sala_id', actividad.sala_id)
    nuevo_aforo_maximo = data.get('aforo_maximo', actividad.aforo_maximo)

    if nuevo_sala_id and nuevo_aforo_maximo is not None:
        sala = db.session.get(Sala, nuevo_sala_id)
        if sala and nuevo_aforo_maximo > sala.capacidad:
            return jsonify({"message": f"El aforo máximo ({nuevo_aforo_maximo}) no puede superar la capacidad de la sala ({sala.capacidad})"}), 400

    actividad.nombre = data.get('nombre', actividad.nombre)
    actividad.descripcion = data.get('descripcion', actividad.descripcion)
    actividad.monitor_id = data.get('monitor_id', actividad.monitor_id)
    actividad.sala_id = nuevo_sala_id
    actividad.horario_id = data.get('horario_id', actividad.horario_id)
    actividad.aforo_maximo = nuevo_aforo_maximo
    db.session.commit()
    return jsonify({"message": "Actividad actualizada con éxito"}), 200

@gym_bp.route('/actividades/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_actividad(id):
    actividad = db.session.get(Actividad, id)
    if not actividad:
        return jsonify({"message": "Actividad no encontrada"}), 404
    db.session.delete(actividad)
    db.session.commit()
    return jsonify({"message": "Actividad eliminada con éxito"}), 200

# --- ENDPOINTS PARA SALAS ---

@gym_bp.route('/salas', methods=['GET'])
def get_salas():
    salas = Sala.query.all()
    return jsonify([{
        "id_sala": s.id_sala,
        "nombre": s.nombre,
        "capacidad": s.capacidad
    } for s in salas]), 200

@gym_bp.route('/salas', methods=['POST'])
@jwt_required()
@admin_required()
def create_sala():
    data = request.get_json()
    capacidad = data.get('capacidad')
    
    if capacidad is not None and capacidad > 10:
        return jsonify({"message": "La capacidad máxima de una sala no puede exceder las 10 personas"}), 400

    nueva_sala = Sala(
        nombre=data.get('nombre'),
        capacidad=capacidad
    )
    db.session.add(nueva_sala)
    db.session.commit()
    return jsonify({"message": "Sala creada con éxito"}), 201

@gym_bp.route('/salas/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_sala(id):
    sala = db.session.get(Sala, id)
    if not sala:
        return jsonify({"message": "Sala no encontrada"}), 404
    data = request.get_json()
    
    nueva_capacidad = data.get('capacidad')
    if nueva_capacidad is not None:
        if nueva_capacidad > 10:
            return jsonify({"message": "La capacidad máxima de una sala no puede exceder las 10 personas"}), 400
        if nueva_capacidad < sala.capacidad:
            actividades_superan = Actividad.query.filter(Actividad.sala_id == id, Actividad.aforo_maximo > nueva_capacidad).first()
            if actividades_superan:
                return jsonify({"message": f"No se puede reducir la capacidad a {nueva_capacidad}. La actividad '{actividades_superan.nombre}' tiene un aforo máximo de {actividades_superan.aforo_maximo}."}), 400

    sala.nombre = data.get('nombre', sala.nombre)
    if nueva_capacidad is not None:
        sala.capacidad = nueva_capacidad
    db.session.commit()
    return jsonify({"message": "Sala actualizada con éxito"}), 200

@gym_bp.route('/salas/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_sala(id):
    sala = db.session.get(Sala, id)
    if not sala:
        return jsonify({"message": "Sala no encontrada"}), 404
    db.session.delete(sala)
    db.session.commit()
    return jsonify({"message": "Sala eliminada con éxito"}), 200

# --- ENDPOINTS PARA HORARIOS ---

@gym_bp.route('/horarios', methods=['GET'])
def get_horarios():
    horarios = Horario.query.all()
    return jsonify([{
        "id_horario": h.id_horario,
        "dia_semana": h.dia_semana,
        "hora_inicio": str(h.hora_inicio),
        "hora_fin": str(h.hora_fin)
    } for h in horarios]), 200

@gym_bp.route('/horarios', methods=['POST'])
@jwt_required()
@admin_required()
def create_horario():
    data = request.get_json()
    from datetime import datetime
    nuevo_horario = Horario(
        dia_semana=data.get('dia_semana'),
        hora_inicio=datetime.strptime(data.get('hora_inicio'), '%H:%M').time(),
        hora_fin=datetime.strptime(data.get('hora_fin'), '%H:%M').time()
    )
    db.session.add(nuevo_horario)
    db.session.commit()
    return jsonify({"message": "Horario creado con éxito"}), 201
