import requests
import os

TAPIT_API_KEY = os.environ.get('TAPIT_API_KEY')

url = "https://api.taap.it/v1/projects"
headers = {
    "Authorization": f"Bearer {TAPIT_API_KEY}"
}

response = requests.get(url, headers=headers)
data = response.json()

print("=== LISTE DE TES PROJETS ===")
if 'items' in data:
    for project in data['items']:
        print(f"📁 Nom: {project.get('name')}")
        print(f"   ID: {project.get('id')}")
        print(f"   Description: {project.get('description', 'Aucune')}")
        print()
else:
    print(data)
