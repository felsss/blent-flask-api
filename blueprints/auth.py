from flask import Blueprint, request, jsonify
from decorators import require_body_parameters
from models import db, User
from datetime import UTC, datetime, timedelta
import jwt
import bcrypt
from config import PREFIX, SALT, JWT_SECRET

bp = Blueprint("auth", __name__, url_prefix=f"{PREFIX}/auth")

@bp.route("/register", methods=['POST'])
@require_body_parameters({'email', 'password', 'nom'})
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
@bp.route("/login", methods=['POST'])
def login():
    body = request.get_json()
    email = body["email"]
    password = body["password"]

    user = User.query.filter_by(email = email).first()

    if  bcrypt.checkpw(password.encode(), user.password_hash):
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
