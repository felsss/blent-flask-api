import requests
import json

def print_response(response):
    print(f"Status: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

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
