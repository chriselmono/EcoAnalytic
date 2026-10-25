from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app) :
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/prueba'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    