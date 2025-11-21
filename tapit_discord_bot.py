import requests
import os
from datetime import datetime

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
    
    # DEBUG: Afficher les champs disponibles du premier lien
    if links and len(links) > 0:
        print(f"🔍 Champs disponibles dans un lien: {list(links[0].keys())}")
    
    # Récupération des stats directement depuis les objets link
    links_stats = {}
    if links:
        for link in links:
            link_name = link.get('name', 'Sans nom')
            
            # Essayer différents noms de champs possibles pour les clics
            clicks = (
                link.get('clicks') or 
                link.get('click_count') or 
                link.get('total_clicks') or 
                link.get('clics') or
                0
            )
            
            print(f"📊 {link_name}: {clicks} clics")
            links_stats[link_name] = clicks
    
    # Envoi sur Discord
    send_to_discord(links_stats)
    print("✅ Terminé!")

if __name__ == "__main__":
    main()
