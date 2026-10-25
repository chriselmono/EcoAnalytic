from functools import wraps

from flask import session, redirect, url_for


def login_required(func):

    @wraps(func)
    def protected_route(*args, **kwargs):

        if 'user_id' not in session:
            return redirect(url_for('user.login'))

        return func(*args, **kwargs)

    return protected_route


def admin_required(func):
    
    @wraps(func)
    def wrapper(*args, **kwargs):

        if 'user_id' not in session:
            return redirect(url_for('user.login'))

        if session.get('rol') != True:
            return redirect(url_for('userDashboard.mi_consumo'))

        return func(*args, **kwargs)

    return wrapper