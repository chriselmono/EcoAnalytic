from flask import Blueprint, render_template

from config.auth import admin_required, login_required
from service.consumoService import ConsumoService
from service.usuariosService import UsuariosService


menuBp = Blueprint("menu", __name__)


@menuBp.route("/")
def index():
    return render_template("index.html")


@menuBp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    # Las consultas sin user_id agregan los consumos de todos los hogares.
    total_kwh = ConsumoService.total_kwh()
    consumo_mensual = ConsumoService.consumo_mensual()
    zonas = sorted(
        ConsumoService.consumo_por_zona(),
        key=lambda zona: zona["consumo"],
        reverse=True,
    )
    variacion = ConsumoService.variacion_mensual()
    alertas = ConsumoService.obtener_alertas()
    ultimos_consumos = ConsumoService.ultimos_consumos()
    total_usuarios = UsuariosService.total_usuarios()
    max_consumo_zona = max(
        (zona["consumo"] for zona in zonas),
        default=0,
    )

    return render_template(
        "dashboard.html",
        page="dashboard",
        total_kwh=round(total_kwh, 2),
        variacion=variacion,
        zonas_activas=len(zonas),
        alertas_activas=len(alertas),
        total_usuarios=total_usuarios,
        consumo_mensual=consumo_mensual,
        zonas=zonas,
        max_consumo_zona=max_consumo_zona,
        alertas=alertas,
        ultimos_consumos=ultimos_consumos,
    )


@menuBp.route("/menu")
@login_required
def menu():
    return render_template("base.html")
