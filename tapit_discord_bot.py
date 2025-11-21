import requests
import os
from datetime import datetime, timedelta

# Récupération des variables d'environnement
TAPIT_API_KEY = os.environ.get('TAPIT_API_KEY')
PROJECT_ID = os.environ.get('PROJECT_ID')
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
    """Récupère les statistiques d'un lien - SANS paramètres de date pour avoir les stats totales"""
    
    url = f"https://api.taap.it/v1/stats/links/{link_id}"
    headers = {
        "Authorization": f"Bearer {TAPIT_API_KEY}"
    }
    
    try:
        # Premier essai : SANS paramètres (pour avoir toutes les stats)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"  📊 Réponse API: {data}")
        
        # La réponse est une liste d'objets stats
        if isinstance(data, list) and len(data) > 0:
            # Additionner tous les total_clicks de tous les objets
            total_clicks = sum(item.get('total_clicks', 0) for item in data)
            return total_clicks
        
        # Si la liste est vide, essayer avec une période (30 derniers jours)
        print(f"  ⚠️ Liste vide, essai avec période de 30 jours...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%dT00:00:00Z"),
            "end_date": end_date.strftime("%Y-%m-%dT23:59:59Z"),
            "max_days": 30
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"  📊 Réponse API (avec dates): {data}")
        
        if isinstance(data, list) and len(data) > 0:
            total_clicks = sum(item.get('total_clicks', 0) for item in data)
            return total_clicks
        
        return 0
    
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erreur stats: {e}")
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
            message += f"👉 **{link_name}:** {clicks:,} clics\n"
            total_clicks += clicks
        
        message += f"\n🔥 **TOTAL:** {total_clicks:,} clics"
    
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
    print(f"🔗 Récupération des liens du projet {PROJECT_ID}...")
    links = get_project_links()
    
    if not links:
        print("❌ Aucun lien trouvé ou erreur")
        send_to_discord(None)
        return
    
    print(f"✅ {len(links)} liens trouvés")
    
    # Récupération des stats de chaque lien
    links_stats = {}
    if links:
        for link in links:
            link_name = link.get('name', 'Sans nom')
            link_id = link.get('id')
            
            if link_id:
                print(f"🔍 Stats pour: {link_name} (ID: {link_id})")
                clicks = get_link_stats(link_id)
                print(f"   ✅ {clicks} clics")
                links_stats[link_name] = clicks
            else:
                print(f"⚠️ Pas d'ID pour: {link_name}")
    
    # Envoi sur Discord
    send_to_discord(links_stats)
    print("✅ Terminé!")

if __name__ == "__main__":
    main()
