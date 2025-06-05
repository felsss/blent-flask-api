from flask import Blueprint, request, jsonify
from decorators import require_body_parameters, require_admin_authentication
from models import db, Product
from config import PREFIX
import logging
import traceback

from flasgger import Swagger

product_logger = logging.getLogger(__name__)

product_bp = Blueprint('produits', __name__, url_prefix=f"{PREFIX}/produits")

@product_bp.route("", methods=['GET'])
@product_bp.route("/", methods=['GET'])
@product_bp.route("/<int:product_id>", methods=['GET'])
def get_product(product_id = None):
    """
    Lister tous les produits ou un produit spécifique identifié par son ID
    ---
    tags:
      - produits
    parameters:
      - in: path
        name: product_id
        type: integer
        required: false
    responses:
      200:
        description: Listing des détails du ou des produits
      404:
        description: Le produit n'existe pas
      500:
        description: Erreur interne
    """
    if request.args.get("id"):
        product_id = request.args.get("id")
    if product_id is not None:
        # Récupérer un produit spécifique (GET /api/produits/{id})
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Produit non trouvé'}), 404
        else:
            return jsonify({
                'id': product.id,
                'nom': product.nom,
                'prix': product.prix,
                'description': product.description,
                'categorie': product.categorie
                }), 200
    else:
        # Récupérer la liste des produits (GET /api/produits)
        products = Product.query.all()
        product_list = []
        for product in products:
            product_list.append({
                'id': product.id,
                'nom': product.nom,
                'prix': product.prix,
                'description': product.description
            })
        return jsonify(product_list), 200

# Ajout d'un nouveau produit
@require_admin_authentication
@require_body_parameters({'id', 'nom', 'description', 'categorie', 'prix'})
@product_bp.route("/", methods=['POST'])
def add_product():
    """
    Ajout d'un produit au catalogue.
    Cet appel nécessite des droits administrateurs.
    ---
    tags:
      - produits
    parameters:
      - in: body
        name: id
        type: integer
        required: true
      - in: body
        name: nom
        type: string
        required: true
      - in: body
        name: description
        type: string
        required: true
      - in: body
        name: categorie
        type: string
        required: true
      - in: body
        name: prix
        type: number
        required: true
      - in: body
        name: quantite_stock
        type: integer
        required: false
        default: 0
    responses:
      200:
        description: Produit ajouté avec succès
      400:
        description: Le produit existe déjà, ou un champ obligatoire est manquant
      500:
        description: Erreur interne
    """
    try:
        body = request.get_json()
        product_logger.debug(f"Création de produit à partir des paramètres suivants : {body}")

        # Vérifier si le produit existe
        product = Product.query.get(body['id'])
        if product:
            return jsonify({'error': 'Produit déjà existant'}), 400

        # On crée le nouveau produit
        quantite_stock = 0
        if 'quantite_stock' in body:
            quantite_stock = body['quantite_stock']
        product = Product(id=body['id'], nom=body['nom'], description=body['description'], categorie=body['categorie'], prix=body['prix'], quantite_stock=quantite_stock)

        # Ajout en base
        db.session.add(product)
        db.session.commit()

        product_logger.info(f"Produit créé avec succès : {product}")
        return jsonify({}), 200

    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Modification d'un produit
@require_admin_authentication
@product_bp.route("/<int:product_id>", methods=["PATCH"])
def modify_product(product_id = None):
    """
    Modification d'un produit déjà présent au catalogue.
    ---
    tags:
      - produits
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
      - in: body
        name: nom
        type: string
        required: false
      - in: body
        name: description
        type: string
        required: false
      - in: body
        name: categorie
        type: string
        required: false
      - in: body
        name: prix
        type: number
        required: false
      - in: body
        name: quantite_stock
        type: integer
        required: false
    responses:
      200:
        description: Produit modifié avec succès
      400:
        description: Le champ ID est manquant
      404:
        description: Le produit n'existe pas
      500:
        description: Erreur interne
    """
    try:
        product_logger.debug(f"Modification de produit à partir des paramètres suivants : {product_id}")
        body = request.get_json()

        if product_id is None:
            return jsonify({'error': 'Champ id manquant'}), 400

        # Vérifier si le produit existe
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Produit non existant'}), 404

        # On modifie le produit suivant les paramètres envoyés
        if "nom" in body:
            product.nom = body["nom"]
        if "description" in body:
            product.description = body["description"]
        if "categorie" in body:
            product.categorie = body["categorie"]
        if "prix" in body:
            product.prix = body["prix"]
        if "quantite_stock" in body:
            product.quantite_stock = body["quantite_stock"]

        # Application de la modif en bdd
        db.session.commit()

        product_logger.info(f"Produit modifié avec succès : {product}")
        return jsonify({}), 200

    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Supprimer un produit
@product_bp.route("/<int:product_id>", methods=["DELETE"])
@require_admin_authentication
def remove_product(product_id = None):
    """
    Suppression d'un produit du catalogue.
    ---
    tags:
      - produits
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
    responses:
      200:
        description: Suppression effectuée avec succès
      400:
        description: Le champ ID est manquant
      404:
        description: Le produit n'existe pas
      500:
        description: Erreur interne
    """
    try:
        product_logger.debug(f"Suppression du produit : {product_id}")
        if product_id is None:
            return jsonify({'error': 'Champ id manquant'}), 400

        # Recherche du produit
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return jsonify({'error': 'Produit non trouvé'}), 404

        # Supprimer le produit
        db.session.delete(product)
        db.session.commit()

        product_logger.info(f"Produit supprimé avec succès : {product}")
        return jsonify({}), 200

    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
