from config.db import db
from datetime import datetime

class Consumo(db.Model):
    __tablename__= 'consumo'
    
    id = db.Column(db.Integer, primary_key=True)
    localidad = db.Column(db.String(255), nullable=False)
    barrio = db.Column(db.String(255), nullable=False)
    kw_consumo = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, nullable=True)
    
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    mes = db.Column(db.String(255), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.user_id'), nullable=False)
    
    alertas = db.relationship('Alerta', backref='consumo', lazy=True)