from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Empleado, db
from app.utils import admin_required

empleados_bp = Blueprint('empleados', __name__)

@empleados_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required()
def get_empleados():
    empleados = Empleado.query.all()
    return jsonify([{
        "id_empleado": e.id_empleado,
        "nombre": e.nombre,
        "email": e.email,
        "rol": e.rol,
        "fecha_contratacion": str(e.fecha_contratacion)
    } for e in empleados]), 200

@empleados_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def crear_empleado():
    data = request.get_json()
    nuevo_empleado = Empleado(
        nombre=data.get('nombre'),
        email=data.get('email'),
        rol=data.get('rol'),
        password_hash="" # El registro completo se hace en auth.py
    )
    db.session.add(nuevo_empleado)
    db.session.commit()
    return jsonify({"message": "Empleado registrado con éxito"}), 201

@empleados_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required()
def actualizar_empleado(id):
    empleado = db.session.get(Empleado, id)
    if not empleado:
        return jsonify({"message": "Empleado no encontrado"}), 404
    data = request.get_json()
    empleado.nombre = data.get('nombre', empleado.nombre)
    empleado.email = data.get('email', empleado.email)
    empleado.rol = data.get('rol', empleado.rol)
    db.session.commit()
    return jsonify({"message": "Empleado actualizado con éxito"}), 200

@empleados_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def eliminar_empleado(id):
    empleado = db.session.get(Empleado, id)
    if not empleado:
        return jsonify({"message": "Empleado no encontrado"}), 404
    db.session.delete(empleado)
    db.session.commit()
    return jsonify({"message": "Empleado eliminado con éxito"}), 200
