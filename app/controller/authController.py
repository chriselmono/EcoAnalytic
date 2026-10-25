from flask import Blueprint, redirect, url_for, session, flash
from authlib.integrations.base_client.errors import OAuthError
from config.oauth import google
from model.usuarios import Usuarios
from config.db import db

authBp = Blueprint('auth', __name__)

@authBp.route('/login/google')
def login_google():
    redirect_uri = url_for('auth.google_callback', _external=True)
    print(redirect_uri)
    return google.authorize_redirect(redirect_uri)

@authBp.route('/google/callback')
def google_callback():
    
    try:

        token = google.authorize_access_token()

        user = token['userinfo']

        google_id = user['sub']
        nombre = user['given_name']
        apellido = user.get('family_name', '')
        correo = user['email']
        foto = user['picture']
        verificado = user['email_verified']

        usuario = Usuarios.query.filter_by(correo=correo).first()

        if not usuario:

            usuario = Usuarios(
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                google_id=google_id,
                foto=foto,
                proveedor='google',
                correo_verificado=verificado
            )

            db.session.add(usuario)
            db.session.commit()

        else:
            # Si tiene un usuario local
            if not usuario.google_id:
                usuario.google_id = google_id
                usuario.foto = foto
                usuario.proveedor = 'Hybrid'

                db.session.commit()

        session['user_id'] = usuario.user_id
        session['nombre'] = usuario.nombre
        session['foto'] = usuario.foto

        return redirect(url_for('userDashboard.mi_consumo'))
    
    except OAuthError as e:
        if e.error == 'access_denied':
            flash("Se canceló el inicio de sesión")
            return redirect(url_for('user.login'))
        
        flash("Error en la autenticación con Google")
        
        return redirect(url_for(user.login))