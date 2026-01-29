#!/usr/bin/env python3
import requests
import sys
import subprocess

# Get API endpoint from Terraform
result = subprocess.run(
    ['terraform', 'output', '-raw', 'api_endpoint'],
    cwd='terraform',
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("❌ Erreur: Impossible de récupérer l'endpoint API")
    print("Exécutez: cd terraform && terraform output api_endpoint")
    sys.exit(1)

api_endpoint = result.stdout.strip()
user_id = sys.argv[1] if len(sys.argv) > 1 else "USER001"

print(f"🔍 Récupération des offres pour {user_id}...")
print(f"📡 Endpoint: {api_endpoint}\n")

response = requests.post(
    f"{api_endpoint}/offers/recommend",
    json={"user_id": user_id},
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ {len(data['recommended_offers'])} offres trouvées:\n")
    
    for i, offer in enumerate(data['recommended_offers'], 1):
        print(f"{i}. {offer['offer_name']}")
        print(f"   Catégorie: {offer['category']}")
        print(f"   Réduction: {offer['discount_value']}% ({offer['discount_type']})")
        print(f"   Score: {offer['score']}")
        print(f"   Stock: {offer['inventory_count']} unités")
        print()
else:
    print(f"❌ Erreur {response.status_code}: {response.text}")
