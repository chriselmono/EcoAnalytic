from model.publicacion import Publicacion
from config.db import db


class PublicacionService:

    # ==========================
    # CREAR PUBLICACIÓN
    # ==========================
    @staticmethod
    def crear_publicacion(data, user_id):

        nueva_publicacion = Publicacion(

            titulo=data['titulo'],

            contenido=data['contenido'],

            categoria=data['categoria'],

            imagen=data.get('imagen'),

            estado=True,

            user_id=user_id
        )

        db.session.add(nueva_publicacion)

        db.session.commit()

        return {
            "success": True
        }

    # ==========================
    # LISTAR PUBLICACIONES
    # ==========================
    @staticmethod
    def obtener_publicaciones():

        publicaciones = Publicacion.query.order_by(
            Publicacion.fecha_publicacion.desc()
        ).all()

        return publicaciones

    # ==========================
    # OBTENER UNA PUBLICACIÓN
    # ==========================
    @staticmethod
    def obtener_publicacion(id):

        publicacion = Publicacion.query.get(id)

        return publicacion

    # ==========================
    # EDITAR PUBLICACIÓN
    # ==========================
    @staticmethod
    def editar_publicacion(id, data):

        publicacion = Publicacion.query.get(id)

        if not publicacion:

            return {
                "error": "Publicación no encontrada"
            }

        publicacion.titulo = data['titulo']

        publicacion.contenido = data['contenido']

        publicacion.categoria = data['categoria']

        publicacion.imagen = data.get('imagen')

        publicacion.estado = data.get('estado', True)

        db.session.commit()

        return {
            "success": True
        }

    # ==========================
    # ELIMINAR PUBLICACIÓN
    # ==========================
    @staticmethod
    def eliminar_publicacion(id):

        publicacion = Publicacion.query.get(id)

        if not publicacion:

            return {
                "error": "Publicación no encontrada"
            }

        db.session.delete(publicacion)

        db.session.commit()

        return {
            "success": True
        }

    # ==========================
    # FILTRAR POR CATEGORÍA
    # ==========================
    @staticmethod
    def publicaciones_por_categoria(categoria):

        publicaciones = Publicacion.query.filter_by(
            categoria=categoria,
            estado=True
        ).order_by(
            Publicacion.fecha_publicacion.desc()
        ).all()

        return publicaciones