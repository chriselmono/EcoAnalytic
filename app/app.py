from flask import Flask
from flask_migrate import Migrate
from config.db import init_db
from config.db import db
from config.oauth import oauth
from controller.usuariosController import user_bp
from controller.menuController import menuBp
from controller.consumoController import consumoBp
from controller.userDashboardController import userDashboardBp
from controller.publicacionController import publicacionBp
from controller.authController import authBp
from controller.desicionController import ml_controller
from controller.mineriaController import mineriaBp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
# Protege sesiones, tokens, mensajes flash, autenticacion, etc.
app.secret_key = os.getenv("SECRET_KEY")

oauth.init_app(app)

init_db(app)
migrate = Migrate(app, db)


# Blueprint es para dividir la aplicación por módulos separados y organizados (y para mejor escalabilidad)
# El register conecta las rutas a la aplicación principal
app.register_blueprint(menuBp)
app.register_blueprint(user_bp)
app.register_blueprint(consumoBp)
app.register_blueprint(userDashboardBp)
app.register_blueprint(publicacionBp)
app.register_blueprint(authBp)
app.register_blueprint(ml_controller)
app.register_blueprint(mineriaBp)

# with app.app_context():
#     from config.db import db
#     db.create_all()
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5000, debug = True)
    