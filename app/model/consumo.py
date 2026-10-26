from datetime import datetime

from config.db import db


class Consumo(db.Model):
    __tablename__ = "consumo"

    id = db.Column(db.Integer, primary_key=True)
    localidad = db.Column(db.String(255), nullable=False)
    barrio = db.Column(db.String(255), nullable=False)
    kw_consumo = db.Column(db.Numeric(10, 2), nullable=False)

    # Primer día del mes facturado; la captura usa formato YYYY-MM.
    # Nullable permite conservar consumos históricos sin periodo confirmado.
    periodo_consumo = db.Column(db.Date, nullable=True)

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Características del hogar cuando se registró este consumo.
    estrato = db.Column(db.Integer, nullable=True)
    personas_vivienda = db.Column(db.Integer, nullable=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.user_id"),
        nullable=False,
    )

    alertas = db.relationship("Alerta", backref="consumo", lazy=True)
