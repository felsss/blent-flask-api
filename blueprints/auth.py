from flask import Blueprint, request, jsonify
from decorators import require_body_parameters
from models import db, User
from datetime import UTC, datetime, timedelta
import jwt
import bcrypt
from config import PREFIX, SALT, JWT_SECRET

from flasgger import Swagger

auth_bp = Blueprint("auth", __name__, url_prefix=f"{PREFIX}/auth")

@require_body_parameters({'email', 'password', 'nom'})
@auth_bp.route("/register", methods=['POST'])
def register():
    """
    Création d'un nouveau compte client
    ---
    tags:
      - auth
    parameters:
      - in: body
        name: email
        type: string
        required: true
      - in: body
        name: password
        type: string
        required: true
      - in: body
        name: nom
        type: string
        required: true
    responses:
      200:
        description: Nouveau compte créé avec succès
      400:
        description: Le compte existe déjà
      500:
        description: Erreur interne
    """
    try:
        body = request.get_json()

        # Vérifier l'adresse email est déjà utilisé pour un compte utilisateur existant
        user = User.query.filter_by(email = body['email']).first()
        if user is not None:
            return jsonify({'error': 'Utilisateur déjà existant avec l\'adresse email fournie.'}), 400

        # Ajouter un nouvel élément au panier
        new_user = User(
            email = body['email'],
            password_hash = bcrypt.hashpw(body['password'].encode(), SALT),
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
@auth_bp.route("/login", methods=['POST'])
def login():
    """
    Login avec un compte client ou admin
    ---
    tags:
      - auth
    parameters:
      - in: body
        name: email
        type: string
        required: true
      - in: body
        name: password
        type: string
        required: true
    responses:
      200:
        description: Login réussi
      401:
        description: Identifiants invalides
    """
    body = request.get_json()
    email = body["email"]
    password = body["password"]

    user = User.query.filter_by(email = email).first()

    if user and bcrypt.checkpw(password.encode(), user.password_hash):
        token = jwt.encode(
            {
                "exp": datetime.now(UTC) + timedelta(hours=1),
                "user": email,
                "id": user.id,
                "role": user.role
            },
            JWT_SECRET,
            algorithm = "HS256"
        )
        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Identifiants invalides."}), 401
