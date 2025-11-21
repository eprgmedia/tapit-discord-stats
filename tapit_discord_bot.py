import requests
import os
from datetime import datetime

# Récupération des variables d'environnement
TAPIT_API_KEY = os.environ.get('TAPIT_API_KEY')
PROJECT_ID = os.environ.get('PROJECT_ID')  # L'ID de ton projet EMPIRE - Affiliation
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def get_project_links():
    """Récupère tous les liens dont le nom commence par EMPIRE"""
    
    url = "https://api.taap.it/v1/links"
    headers = {
        "Authorization": f"Bearer {TAPIT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
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

def get_link_stats(link_id):
    """Récupère les statistiques d'un lien spécifique sur les 30 derniers jours"""
    
    from datetime import datetime, timedelta
    
    # Calculer les dates (30 derniers jours)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    url = f"https://api.taap.it/v1/stats/links/{link_id}"
    headers = {
        "Authorization": f"Bearer {TAPIT_API_KEY}"
    }
    
    params = {
        "start_date": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_date": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "max_days": 30
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # La réponse est une liste, on somme tous les total_clicks
        if isinstance(data, list) and len(data) > 0:
            total_clicks = sum(stat.get('total_clicks', 0) for stat in data)
            return total_clicks
        return 0
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur stats pour {link_id}: {e}")
        return 0

def send_to_discord(links_stats):
    """Envoie les statistiques sur Discord via webhook"""
    
    if not links_stats:
        message = "❌ Erreur lors de la récupération des statistiques"
    else:
        today = datetime.now().strftime("%d/%m/%Y")
        
        # Construction du message avec tous les liens
        message = f"📊 **Statistiques EMPIRE - Affiliation - {today}**\n\n"
        
        total_clicks = 0
        for link_name, clicks in sorted(links_stats.items()):
            message += f"👆 **{link_name}:** {clicks:,} clics\n"
            total_clicks += clicks
        
        message += f"\n📈 **TOTAL:** {total_clicks:,} clics"
    
    payload = {
        "content": message,
        "username": "Tap.it Stats Bot"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("✅ Statistiques envoyées avec succès sur Discord!")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'envoi sur Discord: {e}")

def main():
    print("🚀 Démarrage du bot Tap.it Stats...")
    
    # Vérification des variables d'environnement
    if not all([TAPIT_API_KEY, PROJECT_ID, DISCORD_WEBHOOK_URL]):
        print("❌ Variables d'environnement manquantes!")
        return
    
    # Récupération des liens du projet
    print(f"📥 Récupération des liens du projet {PROJECT_ID}...")
    links = get_project_links()
    
    if not links:
        print("❌ Aucun lien trouvé ou erreur")
        send_to_discord(None)
        return
    
    print(f"✅ {len(links)} liens trouvés")
    
    # Récupération des stats de chaque lien
    links_stats = {}
    for link in links:
        link_id = link.get('id')
        link_name = link.get('name', 'Sans nom')  # Récupère le nom que tu as défini
        
        print(f"📊 Stats pour: {link_name}...")
        clicks = get_link_stats(link_id)
        links_stats[link_name] = clicks
    
    # Envoi sur Discord
    send_to_discord(links_stats)
    print("✅ Terminé!")

if __name__ == "__main__":
    main()
