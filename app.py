import bcrypt
import logging
from flask import Flask, jsonify, url_for
from blueprints import auth, products, orders
from models import db, User, Product
from config import ADMIN_PASSWORD, SALT
from logging.config import dictConfig
#from flask_swagger import swagger
from flasgger import Swagger

app = Flask(__name__)

# Config logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('werkzeug').setLevel(logging.INFO)

# Ajouts des blueprints
app.register_blueprint(auth.auth_bp)
app.register_blueprint(products.product_bp)
app.register_blueprint(orders.order_bp)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///digimarket.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de l'extension SQLAlchemy avec notre application
db.init_app(app)

# Création des tables au démarrage de l'application
@app.before_request
def create_tables():
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()
    app.logger.info("Création des tables OK")

# Création d'un utilisateur de type admin
@app.before_request
def add_admin():
    app.before_request_funcs[None].remove(add_admin)

    # Vérifier si des admins existent déjà
    if User.query.filter_by(role = 'admin').count() == 0:
        admin = User(
            email = 'admin@e.com',
            nom = 'Admin',
            password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode(), SALT),
            role = 'admin',
        )
        db.session.add(admin)
        db.session.commit()
        app.logger.info("Ajout admin réussi")
    else:
        app.logger.debug("Ajout admin déjà fait")

# Ajout de quelques produits pour tester
@app.before_request
def add_sample_data():
    app.before_request_funcs[None].remove(add_sample_data)

    # Vérifier si des produits existent déjà
    if Product.query.count() == 0:
        products = [
            Product(id=111, nom='Smartphone Ultra', description='Smartphone pliable', categorie="Smartphones", prix=799.99, quantite_stock=50),
            Product(id=112, nom='Casque Bluetooth', description='Audio haute qualité', categorie="Casques audio", prix=129.99, quantite_stock=30),
            Product(id=113, nom='Livre Python', description='Apprendre Python en profondeur', categorie="Livres", prix=39.99, quantite_stock=100)
        ]
        db.session.add_all(products)
        db.session.commit()
        app.logger.info("Ajout des produits réussi")
    else:
        app.logger.debug("Ajout des produits déjà fait")

swagger = Swagger(app, template={
    "info": {
        "title": "E-commerce Flask API",
        "description": "Documentation de l'API REST E-commerce",
        "version": "1.0.0"
    }
})
