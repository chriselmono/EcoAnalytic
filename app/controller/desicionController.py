from functools import wraps

from flask import Blueprint, jsonify, render_template, request, session
from config.auth import admin_required, login_required
from model.consumo import Consumo
from service.desicionService import MLService


ml_controller = Blueprint("ml_controller", __name__, url_prefix="/ml")
ml_service = MLService()


def admin_api_required(func):
    """Devuelve códigos HTTP JSON claros para proteger las rutas de la API."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "mensaje": "Debes iniciar sesión."}), 401
        if session.get("rol") not in (True, 1):
            return jsonify(
                {"success": False, "mensaje": "Solo un administrador puede acceder."}
            ), 403
        return func(*args, **kwargs)

    return wrapper


@ml_controller.route("/prediccion", methods=["GET"])
@login_required
@admin_required
def pagina_prediccion():
    registros = (
        Consumo.query.with_entities(Consumo.localidad, Consumo.barrio)
        .filter(Consumo.periodo_consumo.isnot(None))
        .distinct()
        .order_by(Consumo.localidad, Consumo.barrio)
        .all()
    )
    localidades = sorted({localidad for localidad, _ in registros if localidad})
    barrios = sorted({barrio for _, barrio in registros if barrio})
    return render_template(
        "prediccion.html",
        page="prediccion",
        localidades=localidades,
        barrios=barrios,
    )


@ml_controller.route("/estado", methods=["GET"])
@admin_api_required
def estado_modelo():
    registros_validos = Consumo.query.filter(
        Consumo.periodo_consumo.isnot(None)
    ).count()
    return jsonify(
        {
            "success": True,
            "registros_bd": registros_validos,
            "entrenado": ml_service.entrenado,
            "ultimo_periodo_entrenamiento": ml_service.ultimo_periodo_entrenamiento,
        }
    )


@ml_controller.route("/entrenar", methods=["POST"])
@admin_api_required
def entrenar_modelo():
    resultado = ml_service.entrenar_desde_base()
    return jsonify(resultado), (200 if resultado["success"] else 400)


@ml_controller.route("/predecir-localidades", methods=["GET"])
@admin_api_required
def predecir_localidades():
    filtros = {
        "localidad": request.args.get("localidad") or None,
        "barrio": request.args.get("barrio") or None,
    }
    resultado = ml_service.predecir_localidades(filtros=filtros)
    return jsonify(resultado), (200 if resultado["success"] else 400)
