from flask import Blueprint, jsonify
from service.desicionService import MLService

ml_controller = Blueprint("ml_controller", __name__, url_prefix="/ml")
ml_service = MLService()


@ml_controller.route("/entrenar", methods=["POST"])
def entrenar_modelo():
    resultado = ml_service.entrenar_desde_base()
    return jsonify(resultado), (200 if resultado["success"] else 400)


@ml_controller.route("/predecir-localidades", methods=["GET"])
def predecir_localidades():
    resultado = ml_service.predecir_localidades()
    return jsonify(resultado), (200 if resultado["success"] else 400)
