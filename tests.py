import requests
import json

def print_response(response):
    print(f"Status: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

print("#" * 30)
print("Tests de la section 'auth'")
print("=" * 20)
print("Ajout d'un utilisateur incomplet :")
response = requests.post(
    "http://127.0.0.1:5000/api/auth/register",
    json={"email": "zz@a.b", "nom": "Zab"}
)
print_response(response)

print("=" * 20)
print("Ajout d'un utilisateur :")
response = requests.post(
    "http://127.0.0.1:5000/api/auth/register",
    json={"email": "z@a.b", "nom": "Zab", "password": "azerty"}
)
print_response(response)

print("=" * 20)
print("Auth réussie d'un utilisateur :")
response = requests.post(
    "http://127.0.0.1:5000/api/auth/login",
    json={"email": "z@a.b", "password": "azerty"}
)
print_response(response)
# On garde le token pour des requêtes ultérieures
user_token = json.loads(response.content)["token"]

print("=" * 20)
print("Auth échouée d'un utilisateur :")
response = requests.post(
    "http://127.0.0.1:5000/api/auth/login",
    json={"email": "admin@e.com", "password": "azerty"}
)
print_response(response)

print("#" * 30)
print("Tests de la section 'produits'")
print("=" * 20)
print("Liste des produits :")
response = requests.get(
    "http://127.0.0.1:5000/api/produits"
)
print_response(response)

print("=" * 20)
print("Détail du produit 112 :")
response = requests.get(
    "http://127.0.0.1:5000/api/produits?id=112"
)
print_response(response)

print("=" * 20)
print("Détail du produit 113 :")
response = requests.get(
    "http://127.0.0.1:5000/api/produits/113"
)
print_response(response)

response = requests.post(
    "http://127.0.0.1:5000/api/auth/login",
    json={"email": "admin@e.com", "password": "admin"}
)
admin_token = json.loads(response.content)["token"]

print("=" * 20)
print("Ajout d'un produit déjà existant:")
response = requests.post(
    "http://127.0.0.1:5000/api/produits", headers={"Authorization": admin_token},
    json={"id": 113, "nom": "Ecran tip-top", "description": "Le meilleur écran", "categorie" : "Ecrans", "prix": 350}
)
print_response(response)

print("=" * 20)
print("Ajout réussi d'un produit :")
response = requests.post(
    "http://127.0.0.1:5000/api/produits", headers={"Authorization": admin_token},
    json={"id": 114, "nom": "Ecran tip-top", "description": "Le meilleur écran", "categorie" : "Ecrans", "prix": 350}
)
print_response(response)

print("=" * 20)
print("Ajout réussi d'un produit avec quantité :")
response = requests.post(
    "http://127.0.0.1:5000/api/produits", headers={"Authorization": admin_token},
    json={"id": 115, "nom": "Tablette au top", "description": "La meilleure tablette", "categorie" : "Tablette", "prix": 550, "quantite_stock": 25}
)
print_response(response)

print("=" * 20)
print("Suppression réussie d'un produit :")
response = requests.delete(
    "http://127.0.0.1:5000/api/produits/114", headers={"Authorization": admin_token}
)
print_response(response)

print("=" * 20)
print("Modification réussie d'un produit :")
response = requests.patch(
    "http://127.0.0.1:5000/api/produits/115", headers={"Authorization": admin_token},
    json={"nom": "Tablette au top", "description": "La bien meilleure tablette", "categorie" : "Tablette", "prix": 550, "quantite_stock": 25}
)
print_response(response)

print("#" * 30)
print("Tests de la section 'commandes'")
print("=" * 20)
print("Ajout réussi d'une commande :")
response = requests.post(
    "http://127.0.0.1:5000/api/commandes", headers={"Authorization": user_token},
    json={"adresse_livraison": "10 rue de la cave"}
)
print_response(response)
order_id = json.loads(response.content)["id"]

print("=" * 20)
print("Modification réussie d'une commande (ajout d'1 produit à la commande) :")
response = requests.patch(
    f"http://127.0.0.1:5000/api/commandes/{order_id}", headers={"Authorization": user_token},
    json={"produit_id": 115}
)
print_response(response)

print("=" * 20)
print("Modification réussie d'une commande (ajout d'1 produit en quantité à la commande) :")
response = requests.patch(
    f"http://127.0.0.1:5000/api/commandes/{order_id}", headers={"Authorization": user_token},
    json={"produit_id": 111, "quantite": 3}
)
print_response(response)

print("=" * 20)
print("Modification échouée d'une commande (ajout de trop produits à la commande) :")
response = requests.patch(
    f"http://127.0.0.1:5000/api/commandes/{order_id}", headers={"Authorization": user_token},
    json={"produit_id": 115, "quantite": 100}
)
print_response(response)

print("=" * 20)
print("Modification échouée d'une commande (ajout de produit inexistant à la commande) :")
response = requests.patch(
    f"http://127.0.0.1:5000/api/commandes/{order_id}", headers={"Authorization": user_token},
    json={"produit_id": 999, "quantite": 100}
)
print_response(response)

print("=" * 20)
print("Modification échouée d'une commande (changement de statut par un client) :")
response = requests.patch(
    f"http://127.0.0.1:5000/api/commandes/{order_id}", headers={"Authorization": user_token},
    json={"statut": "validée"}
)
print_response(response)

print("=" * 20)
print("Modification échouée d'une commande (changement de statut inexistant) :")
response = requests.patch(
    f"http://127.0.0.1:5000/api/commandes/{order_id}", headers={"Authorization": admin_token},
    json={"statut": "bad_status"}
)
print_response(response)

print("=" * 20)
print("Modification réussie d'une commande (changement de statut) :")
response = requests.patch(
    f"http://127.0.0.1:5000/api/commandes/{order_id}", headers={"Authorization": admin_token},
    json={"statut": "validée"}
)
print_response(response)

print("=" * 20)
print("Modification échouée d'une commande (ajout de produit à une commande déjà validée) :")
response = requests.patch(
    f"http://127.0.0.1:5000/api/commandes/{order_id}", headers={"Authorization": user_token},
    json={"produit_id": 115, "quantite": 10}
)
print_response(response)

print("=" * 20)
print(f"Détail de la commande '{order_id}' :")
response = requests.get(
    f"http://127.0.0.1:5000/api/commandes/{order_id}", headers={"Authorization": user_token}
)
print_response(response)

print("=" * 20)
print("Détails des produits d'une commande (utilisateur) :")
response = requests.get(
    f"http://127.0.0.1:5000/api/commandes/{order_id}/lignes", headers={"Authorization": user_token}
)
print_response(response)

print("=" * 20)
print("Détail de toutes les commandes (utilisateur) :")
response = requests.get(
    "http://127.0.0.1:5000/api/commandes", headers={"Authorization": user_token}
)
print_response(response)

print("=" * 20)
print("Détail de toutes les commandes (admin) :")
response = requests.get(
    "http://127.0.0.1:5000/api/commandes", headers={"Authorization": admin_token}
)
print_response(response)

print("#" * 30)
print("Nettoyage de la base")
response = requests.delete(
    f"http://127.0.0.1:5000/api/commandes/{order_id}", headers={"Authorization": admin_token}
)
print_response(response)
response = requests.delete(
    "http://127.0.0.1:5000/api/produits/114", headers={"Authorization": admin_token}
)
print_response(response)
response = requests.delete(
    "http://127.0.0.1:5000/api/produits/115", headers={"Authorization": admin_token}
)
print_response(response)
