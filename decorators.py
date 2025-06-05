from flask import request
import jwt
from config import JWT_SECRET

def require_body_parameters(required_parameters):
    """
    Requiert que le corps de la requête contienne les champs requis.

    Parameters
    ----------
    required_parameters : list
        Les champs requis.
    """
    def require_body_parameters_inner(func):
        def require_body_parameters_wrapper(**kwargs):
            body = request.get_json()
            required_parameters_set = set(required_parameters)
            fields_set = set(body.keys())
            # Si l'ensemble des champs requis n'est pas inclut dans l'ensemble des champs du corps de la requête
            if not required_parameters_set <= fields_set:
                return {'error': f"Champs manquants: {required_parameters_set} <= {fields_set}"}, 400
            return func(**kwargs)
        return require_body_parameters_wrapper
    return require_body_parameters_inner

def decode_token(token):
    """
    Décode un token.
    """
    try:
        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms="HS256"
        )
    except Exception:
        print("Jeton JWT invalide.")
        return

def require_authentication(f):
    """
    Vérifie que l'utilisateur est authentifié en tant qu'administrateur.
    """
    def require_authentication_wrapper(**kwargs):
        token = request.headers.get("Authorization", "0")
        payload = decode_token(token)
        if not payload:
            return {"error": "Jeton d'accès invalide."}, 401
        return f(**kwargs)
    return require_authentication_wrapper


def require_admin_authentication(f):
    """
    Vérifie que l'utilisateur est authentifié en tant qu'administrateur.
    """
    def require_admin_authentication_wrapper(**kwargs):
        token = request.headers.get("Authorization", "0")
        payload = decode_token(token)
        if not payload:
            return {"error": "Jeton d'accès invalide."}, 401
        else:
            if payload["role"] != "admin":
                return {"error": "Droits insuffisants."}, 401
        return f(**kwargs)
    return require_admin_authentication_wrapper
