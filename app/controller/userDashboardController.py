from flask import Blueprint, render_template, session
from config.auth import login_required

from service.consumoService import ConsumoService

userDashboardBp = Blueprint(
    'userDashboard',
    __name__
)


@userDashboardBp.route('/miDashboard')
@login_required
def mi_consumo():

    user_id = session['user_id']

    total_kwh = ConsumoService.total_kwh(user_id)

    consumo_mensual = ConsumoService.consumo_mensual(user_id)

    variacion = ConsumoService.variacion_mensual(user_id)

    alertas = ConsumoService.obtener_alertas(user_id)

    consumos = ConsumoService.obtener_mis_consumos(user_id)

    zonas = ConsumoService.consumo_por_zona(user_id)

    return render_template(
        'dashboardUsuario.html',

        total_kwh=round(total_kwh, 2),

        consumo_mensual=consumo_mensual,

        variacion=variacion,

        alertas=alertas,

        consumos=consumos,

        zonas=zonas
    )