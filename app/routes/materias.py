from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.materia import Materia

materias_bp = Blueprint('materias', __name__, url_prefix='/api/materias')

@materias_bp.route('/', methods=['POST'])
@jwt_required()
def crear_materia():
    datos = request.get_json()
    nueva_materia = Materia(
        clave=datos['clave'],
        nombre=datos['nombre'],
        creditos=datos['creditos'],
        docente=datos.get('docente', '')
    )
    db.session.add(nueva_materia)
    db.session.commit()
    
    return jsonify({
        "mensaje": "Materia creada",
        "materia": {
            "id": nueva_materia.id,
            "nombre": nueva_materia.nombre
        }
    }), 201