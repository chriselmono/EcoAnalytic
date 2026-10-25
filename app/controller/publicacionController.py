from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from config.auth import (
    login_required,
    admin_required
)

from service.publicacionService import PublicacionService


publicacionBp = Blueprint(
    'publicacion',
    __name__
)

@publicacionBp.route('/publicaciones')
@login_required
def listar_publicaciones():

    publicaciones = (
        PublicacionService.obtener_publicaciones()
    )

    return render_template(
        'publicaciones/listar.html',

        publicaciones=publicaciones,

        page='publicaciones'
    )

@publicacionBp.route(
    '/publicaciones/crear',
    methods=['GET', 'POST']
)
@login_required
@admin_required
def crear_publicacion():

    if request.method == 'POST':

        data = {

            "titulo":
                request.form['titulo'],

            "contenido":
                request.form['contenido'],

            "categoria":
                request.form['categoria']
        }

        PublicacionService.crear_publicacion(
            data,
            session['user_id']
        )

        return redirect(
            url_for(
                'publicacion.listar_publicaciones'
            )
        )

    return render_template(
        'publicaciones/crear.html',

        page='publicaciones'
    )


@publicacionBp.route(
    '/publicaciones/<int:id>'
)
@login_required
def detalle_publicacion(id):

    publicacion = (
        PublicacionService.obtener_publicacion(id)
    )

    return render_template(
        'publicaciones/detalle.html',

        publicacion=publicacion,

        page='publicaciones'
    )


@publicacionBp.route(
    '/publicaciones/editar/<int:id>',
    methods=['GET', 'POST']
)
@login_required
@admin_required
def editar_publicacion(id):

    publicacion = (
        PublicacionService.obtener_publicacion(id)
    )

    if request.method == 'POST':

        data = {

            "titulo":
                request.form['titulo'],

            "contenido":
                request.form['contenido'],

            "categoria":
                request.form['categoria']
        }

        PublicacionService.editar_publicacion(
            id,
            data
        )

        return redirect(
            url_for(
                'publicacion.listar_publicaciones'
            )
        )

    return render_template(
        'publicaciones/editar.html',

        publicacion=publicacion,

        page='publicaciones'
    )


@publicacionBp.route(
    '/publicaciones/eliminar/<int:id>'
)
@login_required
@admin_required
def eliminar_publicacion(id):

    PublicacionService.eliminar_publicacion(id)

    return redirect(
        url_for(
            'publicacion.listar_publicaciones'
        )
    )