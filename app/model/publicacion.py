from config.db import db
from datetime import datetime


class Publicacion(db.Model):

    __tablename__ = 'publicaciones'

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(255), nullable=False)

    contenido = db.Column(db.Text, nullable=False)

    imagen = db.Column(db.String(255), nullable=True)

    categoria = db.Column(
        db.String(100),
        nullable=False
    )

    estado = db.Column(
        db.Boolean,
        default=True
    )

    fecha_publicacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.user_id'),
        nullable=False
    )