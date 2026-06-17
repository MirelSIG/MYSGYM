from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Pago, Usuario, db
from datetime import datetime, timezone

pagos_bp = Blueprint('pagos', __name__)

@pagos_bp.route('/', methods=['POST'])
@jwt_required()
def registrar_pago():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    nuevo_pago = Pago(
        usuario_id=current_user_id,
        monto=data.get('monto'),
        fecha_pago=datetime.now(timezone.utc).date(),
        metodo_pago=data.get('metodo_pago', 'Tarjeta'),
        estado='Completado'
    )
    
    db.session.add(nuevo_pago)
    db.session.commit()
    
    return jsonify({"message": "Pago registrado correctamente"}), 201

@pagos_bp.route('', methods=['GET'])
@jwt_required()
def get_todos_los_pagos():
    pagos = Pago.query.all()
    return jsonify([{
        "id_pago": p.id_pago,
        "usuario": p.usuario.nombre if p.usuario else None,
        "usuario_id": p.usuario_id,
        "fecha_pago": p.fecha_pago.isoformat(),
        "monto": float(p.monto),
        "metodo": p.metodo_pago,
        "estado": p.estado
    } for p in pagos]), 200

@pagos_bp.route('/historial', methods=['GET'])
@jwt_required()
def historial_pagos():
    current_user_id = get_jwt_identity()
    pagos = Pago.query.filter_by(usuario_id=current_user_id).all()
    
    return jsonify([{
        "id_pago": p.id_pago,
        "monto": float(p.monto),
        "fecha": str(p.fecha_pago),
        "metodo": p.metodo_pago,
        "estado": p.estado
    } for p in pagos]), 200

@pagos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_pago(id):
    pago = db.session.get(Pago, id)
    if not pago:
        return jsonify({"message": "Pago no encontrado"}), 404
        
    data = request.get_json()
    pago.monto = data.get('monto', pago.monto)
    pago.estado = data.get('estado', pago.estado)
    pago.metodo_pago = data.get('metodo_pago', pago.metodo_pago)
    
    db.session.commit()
    return jsonify({"message": "Pago actualizado con éxito"}), 200

@pagos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_pago(id):
    pago = db.session.get(Pago, id)
    if not pago:
        return jsonify({"message": "Pago no encontrado"}), 404
        
    db.session.delete(pago)
    db.session.commit()
    return jsonify({"message": "Pago eliminado con éxito"}), 200
