from flask import Blueprint, render_template, request, redirect, url_for, session
from service.usuariosService import UsuariosService

user_bp = Blueprint('user', __name__)

@user_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        data = {
            'nombre': request.form['nombre'],
            'apellido': request.form['apellido'],
            'telefono': request.form['telefono'],
            'correo': request.form['correo'],
            'usuario': request.form['usuario'],
            'password': request.form['password']
        }

        resultado = UsuariosService.registrarUser(data)

        if "error" in resultado:
            return render_template("registro.html", error=resultado["error"])

        return redirect(url_for('user.login'))

    return render_template("registro.html")

# LOGIN

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        
        resultado = UsuariosService.login(usuario, password)
        
        if "error" in resultado:
            return render_template("login.html", error=resultado["error"])
        session['user_id'] = resultado['usuario'].user_id
        session['user_nombre'] = resultado['usuario'].nombre
        rol = resultado['usuario'].rol
        session['rol'] = rol
        session['foto'] = resultado['usuario'].foto
        
        if rol == 1:
            return redirect(url_for('menu.dashboard'))
        else:
            return redirect(url_for('userDashboard.mi_consumo'))
    
    return render_template("login.html")

@user_bp.route('/logout')
def logout():
    session.clear()
    
    return redirect(url_for('user.login'))