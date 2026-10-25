from config.db import db

class Usuarios(db.Model):
    __tablename__= 'usuarios'
    
    user_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellido = db.Column(db.String(255), nullable=True)
    telefono = db.Column(db.Integer, nullable=True)
    correo = db.Column(db.String(255), unique=True, nullable=False)
    usuario = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)
    
    # Usuarios con google
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    foto = db.Column(db.Text, nullable=True)
    proveedor = db.Column(db.String(50), default='local')
    correo_verificado = db.Column(db.Boolean, default=False)
    
    rol = db.Column(db.Boolean, default=False)
    
    consumos = db.relationship(
    'Consumo',
    backref='usuario',
    lazy=True)
    
    alertas = db.relationship('Alerta', backref='usuario', lazy=True)
    
    publicaciones = db.relationship('Publicacion', backref='autor', lazy=True)