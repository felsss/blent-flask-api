from datetime import UTC, datetime, timedelta
import jwt
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from models import db, User, Product

# TODO/FIXME: get from env
JWT_SECRET = "d3fb12750c2eff92120742e1b334479e"

app = Flask(__name__)
bcrypt = Bcrypt(app)

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
    print("Création des tables OK")

# Création d'un utilisateur de type admin
@app.before_request
def add_admin():
    app.before_request_funcs[None].remove(add_admin)

    # Vérifier si des admins existent déjà
    if User.query.filter_by(role = 'admin').count() == 0:
        admin = User(
            email = 'admin@e.com',
            nom = 'Admin',
            password_hash = bcrypt.generate_password_hash
                ('admin').decode('utf-8'),
            role = 'admin',
        )
        db.session.add(admin)
        db.session.commit()
        print("Ajout admin OK")

def require_body_parameters(required_parameters):
    """
    Requiert que le corps de la requête contienne les champs requis.

    Parameters
    ----------
    required_parameters : list
        Les champs requis.
    """
    def inner(func):
        def wrapper(**kwargs):
            body = request.get_json()
            required_parameters_set = set(required_parameters)
            fields_set = set(body.keys())
            # Si l'ensemble des champs requis n'est pas inclut dans l'ensemble des champs du corps de la requête
            if not required_parameters_set <= fields_set:
                return {'error': 'Champs manquants.'}, 400
            return func(**kwargs)
        return wrapper
    return inner

@require_body_parameters({'email', 'password', 'nom'})
@app.route('/api/auth/register', methods=['POST'])
def register_new_user():
    try:
        body = request.get_json()

        # Vérifier l'adresse email est déjà utilisé pour un compte utilisateur existant
        user = User.query.filter_by(email = body['email']).first()
        if user is not None:
            return jsonify({'error': 'Utilisateur déjà existant avec l\'adresse email fournie.'}), 400

        # Ajouter un nouvel élément au panier
        new_user = User(
            email = body['email'],
            password_hash = bcrypt.generate_password_hash
                (body['password']).decode('utf-8'),
            nom = body['nom'],
            role = 'client' # Les comptes admins devront être créés en convertissant manuellement un client en admin directement en base
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@require_body_parameters({'email', 'password'})
@app.route('/api/auth/login', methods=['POST'])
def login():
    body = request.get_json()
    email = body["email"]
    password = body["password"]

    user = User.query.filter_by(email = email).first()
    if bcrypt.check_password_hash(user.password_hash, password):
        token = jwt.encode(
            {
                "exp": datetime.now(UTC) + timedelta(hours=1),
                "user": email,
                "role": user.role
            },
            JWT_SECRET,
            algorithm = "HS256"
        )
        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Mot de passe invalide."}), 401
