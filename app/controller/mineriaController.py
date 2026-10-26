from functools import wraps

from flask import Blueprint, jsonify, render_template, request, session

from config.auth import admin_required, login_required

from service.mineriaService import MineriaService


mineriaBp = Blueprint("mineria", __name__, url_prefix="/mineria")


@mineriaBp.route("/", methods=["GET"])
@login_required
@admin_required
def pagina_mineria():
    """Muestra el módulo de agrupación a usuarios administradores."""
    return render_template("mineria.html", page="mineria")


def admin_api_required(func):
    """Protege las rutas JSON y responde con estado HTTP según el rol."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({
                "success": False,
                "mensaje": "Debes iniciar sesión para acceder a minería de datos.",
            }), 401

        if session.get("rol") not in (True, 1):
            return jsonify({
                "success": False,
                "mensaje": "Solo un administrador puede acceder a esta información.",
            }), 403

        return func(*args, **kwargs)

    return wrapper


@mineriaBp.route("/agrupar-viviendas", methods=["GET"])
@admin_api_required
def agrupar_viviendas():
    """Agrupa los perfiles de consumo actuales con K-means."""
    resultado = MineriaService.agrupar_viviendas(
        cantidad_grupos=request.args.get("grupos", default=3, type=int)
    )
    return jsonify(resultado), (200 if resultado.get("success") else 400)
