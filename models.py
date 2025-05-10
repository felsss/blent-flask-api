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

# class Cart(db.Model):
#     __tablename__ = 'carts'

#     id = db.Column(db.Integer, primary_key=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     # Relation avec les éléments du panier
#     items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

#     def __repr__(self):
#         return f'<Cart {self.id}>'

# class CartItem(db.Model):
#     __tablename__ = 'cart_items'

#     id = db.Column(db.Integer, primary_key=True)
#     cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
#     product_id = db.Column(db.String(10), db.ForeignKey('products.id'), nullable=False)
#     quantity = db.Column(db.Integer, default=1)

#     # Relation avec le produit
#     product = db.relationship('Product', backref='cart_items')

#     def __repr__(self):
#         return f'<CartItem {self.id}, Product: {self.product_id}, Qty: {self.quantity}>'
