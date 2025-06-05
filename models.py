from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# Initialisation de l'extension SQLAlchemy
db = SQLAlchemy()

# Modèle pour les utilisateurs (clients et admins)
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<User: id={self.id}, email={self.email}, nom={self.nom} role={self.role}>'

# Modèle pour les produits
class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(50), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    quantite_stock = db.Column(db.Integer, default=0)
    date_creation = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Product: id={self.id}, nom={self.nom}, categorie={self.categorie}, prix={self.prix}, stock={self.quantite_stock}>'

class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_commande = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    adresse_livraison = db.Column(db.String(200), nullable=False)
    statut = db.Column(db.String(20)) # en attente, validée, expédiée, annulée

    # Relation avec les éléments produit de la commande
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order: id={self.id}, utilisateur_id={self.utilisateur_id}, date_commande={self.date_commande}, adresse_livraison={self.adresse_livraison}, statut={self.statut}>'

class OrderItem(db.Model):
    __tablename__ = 'order_item'

    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)

    # Relation avec le produit
    product = db.relationship('Product', backref='order_item')

    def __repr__(self):
        return f'<OrderItem {self.id}, commande_id={self.commande_id}, produit_id={self.produit_id}, quantite={self.quantite}>'
