from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from config.auth import login_required
from service.consumoService import ConsumoService


consumoBp = Blueprint("consumo", __name__)


@consumoBp.route("/consumos")
@login_required
def listar_consumos():
    consumos = ConsumoService.obtener_consumos(session["user_id"])
    return render_template("historialConsumo.html", consumos=consumos)


@consumoBp.route("/consumos/crear", methods=["GET", "POST"])
@login_required
def crear_consumo():
    if request.method == "POST":
        data = {
            "localidad": request.form.get("localidad"),
            "barrio": request.form.get("barrio"),
            "kw_consumo": request.form.get("kw_consumo"),
            "periodo_consumo": request.form.get("periodo_consumo"),
            "estrato": request.form.get("estrato"),
            "personas_vivienda": request.form.get("personas_vivienda"),
        }

        try:
            ConsumoService.crear_consumo(data, session["user_id"])
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("consumo.crear_consumo"))

        flash("Consumo registrado correctamente.", "success")
        return redirect(url_for("consumo.listar_consumos"))

    return render_template(
        "crearConsumo.html",
        localidades=ConsumoService.LOCALIDADES_BOGOTA,
    )


@consumoBp.route("/consumos/plantilla", methods=["GET"])
@login_required
def descargar_plantilla_consumos():
    plantilla = ConsumoService.generar_plantilla_excel()
    return send_file(
        plantilla,
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        as_attachment=True,
        download_name="plantilla_consumos.xlsx",
    )


@consumoBp.route("/consumos/masivo", methods=["POST"])
@login_required
def cargar_consumos_masivos():
    archivo = request.files.get("archivo")
    resultado = ConsumoService.importar_consumos_excel(
        archivo,
        session["user_id"],
    )
    return jsonify(resultado), (200 if resultado["success"] else 400)


@consumoBp.route("/consumos/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_consumo(id):
    consumo = ConsumoService.obtener_consumo(id, session["user_id"])
    if consumo is None:
        flash("El consumo no existe o no tienes permiso para editarlo.", "error")
        return redirect(url_for("consumo.listar_consumos"))

    if request.method == "POST":
        data = {
            "localidad": request.form.get("localidad"),
            "barrio": request.form.get("barrio"),
            "kw_consumo": request.form.get("kw_consumo"),
            "periodo_consumo": request.form.get("periodo_consumo"),
            "estrato": request.form.get("estrato"),
            "personas_vivienda": request.form.get("personas_vivienda"),
        }
        try:
            ConsumoService.editar_consumo(id, data, session["user_id"])
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("consumo.editar_consumo", id=id))
        except Exception:
            flash("No se pudieron guardar los cambios. Inténtalo de nuevo.", "error")
            return redirect(url_for("consumo.editar_consumo", id=id))

        flash("Consumo actualizado correctamente.", "success")
        return redirect(url_for("consumo.listar_consumos"))

    return render_template(
        "editarConsumo.html",
        consumo=consumo,
        localidades=ConsumoService.LOCALIDADES_BOGOTA,
        page="historial",
    )


@consumoBp.route("/consumos/eliminar/<int:id>")
@login_required
def eliminar_consumo(id):
    resultado = ConsumoService.eliminar_consumo(id, session["user_id"])

    if "error" in resultado:
        flash(resultado["error"], "error")
    else:
        flash(resultado["success"], "success")

    return redirect(url_for("consumo.listar_consumos"))
