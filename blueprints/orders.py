from flask import Blueprint, request, jsonify
from decorators import require_body_parameters, require_authentication, decode_token, require_admin_authentication
from models import db, Order, OrderItem, Product
from config import PREFIX
import logging
import traceback

VALID_STATUSES = ("en attente", "validée", "expédiée", "annulée")

order_logger = logging.getLogger(__name__)

order_bp = Blueprint('commandes', __name__, url_prefix=f"{PREFIX}/commandes")

# Renvoie le payload du token
def get_payload():
    token = request.headers.get("Authorization", "0")
    return decode_token(token)

# Renvoie l'ID utilisateur à partir du token
def get_user_id():
    payload = get_payload()
    if payload and "id" in payload:
        return payload["id"]

# Renvoie le rôle de l'utilisateur
def get_user_role():
    payload = get_payload()
    if payload and "role" in payload:
        return payload["role"]

# Lister les commandes :
# Si admin, toutes les commandes
# Si client, ses propres commandes
@require_authentication
@order_bp.route("", methods=['GET'])
@order_bp.route("/", methods=['GET'])
@order_bp.route("/<int:order_id>", methods=['GET'])
def get_order(order_id = None):
    """
    Lister toutes les commandes ou une commande spécifique identifiée par son ID
    ---
    tags:
      - commandes
    parameters:
      - in: path
        name: order_id
        type: integer
        required: false
    responses:
      200:
        description: Listing des détails de la ou des commandes
      403:
        description: L'accès aux détails de cette commande n'est pas autorisé
      404:
        description: La commande n'existe pas
      500:
        description: Erreur interne
    """
    try:
        user_role = get_user_role()
        utilisateur_id = get_user_id()
        if request.args.get("id"):
            order_id = request.args.get("id")
        if order_id is not None:
            # Récupérer une commande spécifique
            order = Order.query.get(order_id)
            if not order:
                return jsonify({'error': 'Commande non trouvée'}), 404
            else:
                if user_role == "admin" or utilisateur_id == order.utilisateur_id:
                    return jsonify({
                        'id': order.id,
                        'utilisateur_id': order.utilisateur_id,
                        'date_commande': order.date_commande,
                        'adresse_livraison': order.adresse_livraison,
                        'statut': order.statut
                        }), 200
                else:
                    return jsonify({'error': f"La commande n'appartient pas à l'utilisateur {utilisateur_id}"}), 403
        else:
            if user_role == "admin":
                # On renvoie toutes les commandes
                orders = Order.query.all()
            else:
                # On renvoie les commandes de l'utilisateur
                orders = Order.query.filter_by(utilisateur_id=utilisateur_id).all()
            order_list = []
            for order in orders:
                order_list.append({
                    'id': order.id,
                    'utilisateur_id': order.utilisateur_id,
                    'date_commande': order.date_commande,
                    'adresse_livraison': order.adresse_livraison,
                    'statut': order.statut
                })
            return jsonify(order_list), 200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Consulter les lignes d'une commande (GET /api/commandes/{id}/lignes)
@require_authentication
@order_bp.route("/<int:order_id>/lignes", methods=['GET'])
def get_order_lines(order_id = None):
    """
    Lister les produits d'une commande spécifique identifiée par son ID
    ---
    tags:
      - commandes
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
    responses:
      200:
        description: Listing des produits de la commande
      400:
        description: Le champ ID est manquant
      403:
        description: L'accès aux détails de cette commande n'est pas autorisé
      404:
        description: La commande n'existe pas
      500:
        description: Erreur interne
    """
    try:
        user_role = get_user_role()
        utilisateur_id = get_user_id()
        if order_id is not None:
            # Récupérer une commande spécifique
            order = Order.query.get(order_id)
            if not order:
                return jsonify({'error': 'Commande non trouvée'}), 404
            else:
                if user_role == "admin" or utilisateur_id == order.utilisateur_id:
                    # On récupère les items de la commande
                    order_items = OrderItem.query.filter_by(commande_id=order.id).all()
                    order_items_list = []
                    for order_item in order_items:
                        order_items_list.append({
                            'produit_id': order_item.produit_id,
                            'quantite': order_item.quantite,
                            'prix_unitaire': order_item.prix_unitaire,
                        })
                    return jsonify(order_items_list), 200
                else:
                    return jsonify({'error': f"La commande n'appartient pas à l'utilisateur {utilisateur_id}"}), 403
        else:
            return jsonify({'error': 'ID de commande manquant'}), 400

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Créer une nouvelle commande (POST /api/commandes)
@require_body_parameters({'adresse_livraison'})
@require_authentication
@order_bp.route("/", methods=["POST"])
def add_order():
    """
    Création d'une nouvelle commande
    ---
    tags:
      - commandes
    parameters:
      - in: body
        name: adresse_livraison
        type: string
        required: true
    responses:
      200:
        description: Commande créée avec succès
        schema:
          type: object
          properties:
            id:
              type: integer
              description: L'ID de la commande créée
      400:
        description: Le champ adresse_livraison est manquant
      500:
        description: Erreur interne
    """
    try:
        body = request.get_json()
        order_logger.debug(f"Création d'une nouvelle commande avec les paramètres suivants : {body}")

        # Retrouver l'id de l'utilisateur connecté
        utilisateur_id = get_user_id()

        # On crée la nouvelle commande
        order = Order(utilisateur_id=utilisateur_id, adresse_livraison=body['adresse_livraison'], statut="en attente")

        # Ajout en base
        db.session.add(order)
        db.session.commit()

        order_logger.info(f"Commande créée avec succès : {order}")
        return jsonify({"id": order.id}), 200

    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Modification d'une commande
# Cas 1: par un utilisateur -> peut ajouter des produits à la commande, si elle est en statut "en attente"
# Cas 2: par un admin -> peut changer le statut de la commande
@require_authentication
@order_bp.route("/<int:order_id>", methods=["PATCH"])
def modify_order(order_id = None):
    """
    Modification d'une commande (changement de statut par un admin, ou ajout de produits par un client)
    ---
    tags:
      - commandes
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
      - in: body
        name: statut
        type: string
        required: false
      - in: body
        name: produit_id
        type: integer
        required: false
      - in: body
        name: quantite
        type: integer
        required: false
    responses:
      200:
        description: Commande modifiée avec succès
      400:
        description: Le champ ID est manquant ou modification impossible (voir détails dans la réponse de l'API)
      403:
        description: L'accès aux détails de cette commande n'est pas autorisé
      404:
        description: La commande n'existe pas, le nouveau statut n'existe pas, le produit à ajouter n'existe pas
      500:
        description: Erreur interne
    """
    try:
        if order_id is None:
            return jsonify({'error': 'Champ id manquant'}), 400

        # Recherche de la commande
        order = Order.query.filter_by(id=order_id).first()
        if not order:
            return jsonify({'error': 'Commande non trouvé'}), 404
        order_item = None

        # Retrouver le rôle de l'utilisateur connecté
        user_role = get_user_role()

        body = request.get_json()
        order_logger.debug(f"Modification de la commande '{order_id}' par un utilisateur de type '{user_role}' avec les paramètres suivants : {body}")

        if user_role == "admin" and "statut" in body:
            if body["statut"] in VALID_STATUSES:
                nouveau_statut = body["statut"]
                # Mettre à jour le stock des produits de la commande si passage du statut de "en attente" à "validée"
                if order.statut == "en attente" and nouveau_statut == "validée":
                    order_items = OrderItem.query.filter_by(commande_id=order_id).all()
                    for order_item in order_items:
                        order_logger.debug(f"Mise à jour de la quantité produit pour le produit {order_item.produit_id} de la commande {order_id}")
                        Product.query.filter_by(id=order_item.produit_id).update({"quantite_stock": Product.quantite_stock - order_item.quantite})
                order.statut = nouveau_statut
            else:
                return jsonify({'error': 'Statut de commande non existant'}), 404
        elif user_role == "client" and "produit_id" in body:
            product = Product.query.get(body['produit_id'])
            if not product:
                return jsonify({'error': 'Produit non existant'}), 404
            utilisateur_id = get_user_id()
            if utilisateur_id != order.utilisateur_id:
                return jsonify({'error': f"La commande n'appartient pas à l'utilisateur {utilisateur_id}"}), 403
            if order.statut != "en attente":
                return jsonify({'error': f'La commande est en statut {order.statut}'}), 400
            quantity = 1
            if "quantite" in body:
                quantity = body["quantite"]
            if quantity > product.quantite_stock:
                return jsonify({'error': f'Quantité stock de produit insuffisante {quantity} > {product.quantite_stock}'}), 400
            order_item = OrderItem(commande_id=order.id, produit_id=body['produit_id'], quantite=quantity, prix_unitaire=product.prix)
            db.session.add(order_item)
        else:
            return jsonify({'error': f"Modification de commande impossible: paramètres '{body}' incompatibles avec le rôle '{user_role}'"}), 400

        # Application des modifs en base
        db.session.commit()

        order_logger.info(f"Commande modifiée avec succès : {order} / {order_item}")
        return jsonify({}), 200

    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Supprimer une commande
@order_bp.route("/<int:order_id>", methods=["DELETE"])
@require_admin_authentication
def remove_order(order_id = None):
    """
    Suppression d'une commande
    ---
    tags:
      - commandes
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
    responses:
      200:
        description: Suppression effectuée avec succès
      400:
        description: Le champ ID est manquant
      404:
        description: La commande n'existe pas
      500:
        description: Erreur interne
    """
    try:
        order_logger.debug(f"Suppression de la commande : {order_id}")
        if order_id is None:
            return jsonify({'error': 'Champ id manquant'}), 400

        # Recherche de la commande
        order = Order.query.filter_by(id=order_id).first()
        if not order:
            return jsonify({'error': 'Commande non trouvé'}), 404

        # Supprimer la commande
        db.session.delete(order)
        db.session.commit()

        order_logger.info(f"Commande supprimé avec succès : {order}")
        return jsonify({}), 200

    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
