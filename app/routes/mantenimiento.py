from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Material, Incidencia, db
from datetime import datetime, timezone
from app.utils import admin_required

mantenimiento_bp = Blueprint('mantenimiento', __name__)

# --- ENDPOINTS PARA MATERIALES ---

@mantenimiento_bp.route('/materiales', methods=['GET'])
def get_materiales():
    materiales = Material.query.all()
    return jsonify([{
        "id_material": m.id_material,
        "nombre": m.nombre,
        "estado": m.estado,
        "sala": m.sala.nombre if m.sala else "General",
        "sala_id": m.sala_id
    } for m in materiales]), 200

@mantenimiento_bp.route('/materiales', methods=['POST'])
@jwt_required()
@admin_required()
def crear_material():
    data = request.get_json()
    nuevo_material = Material(
        nombre=data.get('nombre'),
        estado=data.get('estado', 'Bueno'),
        sala_id=data.get('sala_id')
    )
    db.session.add(nuevo_material)
    db.session.commit()
    return jsonify({"message": "Material registrado con éxito"}), 201

@mantenimiento_bp.route('/materiales/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required()
def actualizar_material(id):
    material = db.session.get(Material, id)
    if not material:
        return jsonify({"message": "Material no encontrado"}), 404
    data = request.get_json()
    material.nombre = data.get('nombre', material.nombre)
    material.estado = data.get('estado', material.estado)
    material.sala_id = data.get('sala_id', material.sala_id)
    db.session.commit()
    return jsonify({"message": "Material actualizado con éxito"}), 200

@mantenimiento_bp.route('/materiales/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def eliminar_material(id):
    material = db.session.get(Material, id)
    if not material:
        return jsonify({"message": "Material no encontrado"}), 404
    db.session.delete(material)
    db.session.commit()
    return jsonify({"message": "Material eliminado con éxito"}), 200

# --- ENDPOINTS PARA INCIDENCIAS ---

@mantenimiento_bp.route('/incidencias', methods=['POST'])
@jwt_required()
# Aquí permitimos que tanto clientes como empleados reporten incidencias
def reportar_incidencia():
    data = request.get_json()
    nueva_incidencia = Incidencia(
        descripcion=data.get('descripcion'),
        material_id=data.get('material_id'),
        empleado_id=data.get('empleado_id'),
        fecha=datetime.now(timezone.utc).date(),
        estado='pendiente'
    )
    db.session.add(nueva_incidencia)
    db.session.commit()
    return jsonify({"message": "Incidencia reportada con éxito"}), 201

@mantenimiento_bp.route('/incidencias', methods=['GET'])
@jwt_required()
@admin_required()
# Solo los empleados pueden ver la lista completa de incidencias
def listar_incidencias():
    incidencias = Incidencia.query.all()
    return jsonify([{
        "id_incidencia": i.id_incidencia,
        "descripcion": i.descripcion,
        "material": i.material.nombre if i.material else "Desconocido",
        "material_id": i.material_id,
        "empleado": i.empleado.nombre if i.empleado else "Sin asignar",
        "empleado_id": i.empleado_id,
        "estado": i.estado,
        "fecha": str(i.fecha)
    } for i in incidencias]), 200

@mantenimiento_bp.route('/incidencias/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required()
def actualizar_incidencia(id):
    incidencia = db.session.get(Incidencia, id)
    if not incidencia:
        return jsonify({"message": "Incidencia no encontrada"}), 404
    data = request.get_json()
    incidencia.descripcion = data.get('descripcion', incidencia.descripcion)
    incidencia.estado = data.get('estado', incidencia.estado)
    incidencia.empleado_id = data.get('empleado_id', incidencia.empleado_id)
    db.session.commit()
    return jsonify({"message": "Incidencia actualizada con éxito"}), 200
