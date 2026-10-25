from model.usuarios import Usuarios
from config.db import db
from werkzeug.security import generate_password_hash, check_password_hash

class UsuariosService:
    @staticmethod
    def registrarUser(data):
        existeCorreo = Usuarios.query.filter_by(correo=data['correo']).first()
        existeUser = Usuarios.query.filter_by(usuario=data['usuario']).first()
        
        if existeCorreo or existeUser:
            return {"error": "Correo o usuario ya registrado"}
        
        nuevoUser = Usuarios(
            nombre=data['nombre'],  
            apellido=data['apellido'],  
            telefono=data['telefono'],  
            correo=data['correo'],  
            usuario=data['usuario'],  
            password=generate_password_hash(data['password']),  
            rol=False
        )
        
        db.session.add(nuevoUser)
        db.session.commit()
        
        return {"success": True}
    
    @staticmethod
    def login(usuario, password):
        existeUser = Usuarios.query.filter_by(usuario=usuario).first()
        
        if not existeUser:
            return {"error": "El usuario no está registrado"}
        
        if not check_password_hash(existeUser.password, password):
            return {"error": "Contraseña incorrecta"}
        
        return {
            "success": True,
            "usuario": existeUser
        }
        
    @staticmethod
    def total_usuarios():
        total = Usuarios.query.count()
        
        return total