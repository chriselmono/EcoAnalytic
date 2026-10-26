from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from service.consumoService import ConsumoService
from config.auth import login_required

consumoBp = Blueprint('consumo', __name__)


@consumoBp.route('/consumos')
@login_required
def listar_consumos():
    consumos = ConsumoService.obtener_consumos(session['user_id'])
    return render_template('historialConsumo.html', consumos=consumos)


@consumoBp.route('/consumos/crear', methods=['GET', 'POST'])
@login_required
def crear_consumo():
    if request.method == 'POST':
        data = {
            'localidad': request.form['localidad'],
            'barrio': request.form['barrio'],
            'kw_consumo': request.form['kw_consumo'],
            'periodo_consumo': request.form['periodo_consumo'],
            'estrato': request.form.get('estrato'),
            'personas_vivienda': request.form.get('personas_vivienda'),
        }

        try:
            ConsumoService.crear_consumo(data, session['user_id'])
        except ValueError as error:
            flash(str(error), 'error')
            return redirect(url_for('consumo.crear_consumo'))

        return redirect(url_for('consumo.listar_consumos'))

    return render_template('crearConsumo.html')


@consumoBp.route('/consumos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_consumo(id):
    consumo = ConsumoService.obtener_consumo(id, session['user_id'])

    if request.method == 'POST':
        data = {
            'localidad': request.form['localidad'],
            'barrio': request.form['barrio'],
            'kw_consumo': request.form['kw_consumo'],
            'periodo_consumo': request.form['periodo_consumo'],
            'estrato': request.form.get('estrato'),
            'personas_vivienda': request.form.get('personas_vivienda'),
        }

        ConsumoService.editar_consumo(id, data, session['user_id'])
        return redirect(url_for('consumo.listar_consumos'))

    return render_template('editar_consumo.html', consumo=consumo)


@consumoBp.route('/consumos/eliminar/<int:id>')
@login_required
def eliminar_consumo(id):
    resultado = ConsumoService.eliminar_consumo(id, session['user_id'])

    if "error" in resultado:
        flash(resultado["error"], "error")
    else:
        flash(resultado["success"], "success")

    return redirect(url_for('consumo.listar_consumos'))
