from config.db import db
from datetime import datetime


class Alerta(db.Model):

    __tablename__ = 'alertas'

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(
        db.String(255),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=False
    )

    tipo = db.Column(
        db.String(50),
        nullable=False
    )

    estado = db.Column(
        db.String(50),
        default='pendiente'
    )

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.user_id'),
        nullable=False
    )

    consumo_id = db.Column(
        db.Integer,
        db.ForeignKey('consumo.id'),
        nullable=True
    )