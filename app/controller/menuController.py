from flask import Blueprint, render_template, redirect, url_for, session

from config.auth import login_required
from config.auth import admin_required
from service.consumoService import ConsumoService
from service.usuariosService import UsuariosService

menuBp = Blueprint('menu', __name__)

@menuBp.route('/')
def index():
    return render_template("index.html")

@menuBp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    usuario_id = session['user_id']

    total_kwh = ConsumoService.total_kwh(usuario_id)

    consumo_mensual = ConsumoService.consumo_mensual(usuario_id)

    zonas = ConsumoService.consumo_por_zona(usuario_id)

    variacion = ConsumoService.variacion_mensual(usuario_id)

    alertas = ConsumoService.obtener_alertas(usuario_id)

    ultimos_consumos = ConsumoService.ultimos_consumos(usuario_id)

    usuarios_activos = UsuariosService.total_usuarios()

    return render_template(
        'dashboard.html',

        total_kwh=round(total_kwh, 2),

        variacion=variacion,

        zonas_activas=len(zonas),

        alertas_activas=len(alertas),

        usuarios_activos=usuarios_activos,

        consumo_mensual=consumo_mensual,

        zonas=zonas,

        alertas=alertas,

        ultimos_consumos=ultimos_consumos
    )
    
@menuBp.route('/menu')
@login_required
def menu():
    return render_template('base.html')