import requests
import json

def print_response(response):
    print(f"Status: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

# Register/Auth
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

print("=" * 20)
print("Auth échouée d'un utilisateur :")
response = requests.post(
    "http://127.0.0.1:5000/api/auth/login",
    json={"email": "admin@e.com", "password": "azerty"}
)
print_response(response)

# Lister des produits
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

# Gestion des produits
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
print("Ajout échoué d'un produit :")
response = requests.post(
    "http://127.0.0.1:5000/api/produits", headers={"Authorization": admin_token},
    json={"id": 114, "nom": "Ecran tip-top", "description": "Le meilleur écran"}
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





# Nettoyage base de test
# response = requests.delete(
#     "http://127.0.0.1:5000/api/produits/114", headers={"Authorization": admin_token}
# )
# response = requests.delete(
#     "http://127.0.0.1:5000/api/produits/115", headers={"Authorization": admin_token}
# )
