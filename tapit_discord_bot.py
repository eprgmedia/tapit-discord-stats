import requests
import os
from datetime import datetime, timedelta

# Variables d'environnement
TAPIT_API_KEY = os.environ.get('TAPIT_API_KEY')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
PROJECT_ID = os.environ.get('PROJECT_ID')

def get_project_links():
    """Récupère tous les liens du projet"""
    
    url = "https://api.taap.it/v1/links"
    headers = {
        "Authorization": f"Bearer {TAPIT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    params = {
        "project_id": PROJECT_ID,
        "page_size": 100
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"📦 Structure de la réponse API: {type(data)}")
        
        # Gérer différents formats de réponse
        if isinstance(data, dict):
            all_links = data.get('items', data.get('data', data.get('links', [])))
        elif isinstance(data, list):
            all_links = data
        else:
            print(f"❌ Format de réponse inattendu: {type(data)}")
            return None
        
        # Filtrer uniquement les liens dont le nom commence par "EMPIRE"
        project_links = [link for link in all_links if link.get('name', '').startswith('EMPIRE')]
        
        print(f"✅ {len(project_links)} liens trouvés commençant par 'EMPIRE'")
        return project_links
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération des liens: {e}")
        return None

def send_to_discord(links_stats):
    """Envoie les statistiques sur Discord via webhook"""
    
    if not links_stats:
        message = "❌ Aucune statistique disponible"
    else:
        today = datetime.now().strftime("%d/%m/%Y")
        
        # Tri par nombre de clics décroissant
        sorted_stats = sorted(links_stats, key=lambda x: x['clicks'], reverse=True)
        
        message = f"📊 **Statistiques EMPIRE - Affiliation - {today}**\n\n"
        
        total = sum(stat['clicks'] for stat in sorted_stats)
        message += f"🔥 **TOTAL : {total:,} clics**\n\n"
        
        for stat in sorted_stats:
            message += f"👉 **{stat['name']}** : {stat['clicks']:,} clics\n"
    
    payload = {
        "content": message,
        "username": "Tap.it Stats Bot"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("✅ Stats envoyées sur Discord!")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur Discord: {e}")

def main():
    print("🚀 Démarrage du bot Tap.it Stats...")
    
    # Récupération des liens
    print(f"📋 Récupération des liens du projet {PROJECT_ID}...")
    links = get_project_links()
    
    if not links:
        print("❌ Aucun lien trouvé!")
        return
    
    # Filtrer les liens EMPIRE
    empire_links = [link for link in links if 'EMPIRE' in link.get('name', '')]
    print(f"✅ {len(empire_links)} liens EMPIRE trouvés")
    
    # CORRECTION FINALE : Utiliser directement le champ 'clicks' de chaque lien
    # Pas besoin d'appeler l'API stats !
    links_stats = []
    for i, link in enumerate(empire_links):
        link_name = link['name']
        
        # DEBUG : Afficher TOUS les champs du premier lien pour diagnostic
        if i == 0:
            print(f"🔍 DIAGNOSTIC - Tous les champs disponibles dans un lien:")
            for key, value in link.items():
                print(f"   - {key}: {value}")
        
        clicks = link.get('clicks', 0)  # Le champ clicks est DÉJÀ dans la réponse !
        
        print(f"✅ {link_name}: {clicks} clics")
        
        links_stats.append({
            'name': link_name,
            'clicks': clicks
        })
    
    # Envoi sur Discord
    send_to_discord(links_stats)
    print("✅ Terminé!")

if __name__ == "__main__":
    main()
