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
    params = {
        "project_id": PROJECT_ID,
        "page_size": 100
    }
    headers = {
        "Authorization": f"Bearer {TAPIT_API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return []

def get_link_stats(link_id, link_name):
    """Récupère les stats d'un lien spécifique"""
    
    # Dates : du début à aujourd'hui
    start_date = "2024-01-01"  # Date large pour être sûr
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    # ESSAI 1 : Endpoint sans /summary
    url = f"https://api.taap.it/v1/stats/links/{link_id}"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "max_days": 30
    }
    headers = {
        "Authorization": f"Bearer {TAPIT_API_KEY}"
    }
    
    try:
        print(f"🔄 Tentative pour {link_name}...")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # L'endpoint retourne un array de stats quotidiennes
            # On doit sommer tous les total_clicks
            total_clicks = 0
            if isinstance(data, list):
                for day_stat in data:
                    total_clicks += day_stat.get('total_clicks', 0)
            else:
                total_clicks = data.get('total_clicks', 0)
            
            print(f"✅ {link_name}: {total_clicks} clics")
            return total_clicks
        
        elif response.status_code == 403:
            print(f"⚠️ {link_name}: 403 Forbidden - Accès refusé")
            return 0
            
        elif response.status_code == 404:
            print(f"⚠️ {link_name}: 404 - Pas de stats disponibles")
            return 0
            
        else:
            print(f"⚠️ {link_name}: Status {response.status_code}")
            return 0
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur stats pour {link_name}: {e}")
        return 0

def send_to_discord(links_stats):
    """Envoie les statistiques sur Discord"""
    
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
            message += f"• **{stat['name']}** : {stat['clicks']:,} clics\n"
    
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
    
    # Récupération des stats
    links_stats = []
    for link in empire_links:
        link_id = link['id']
        link_name = link['name']
        
        clicks = get_link_stats(link_id, link_name)
        links_stats.append({
            'name': link_name,
            'clicks': clicks
        })
    
    # Envoi sur Discord
    send_to_discord(links_stats)
    print("✅ Terminé!")

if __name__ == "__main__":
    main()
