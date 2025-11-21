import requests
import os
from datetime import datetime

# Récupération des variables d'environnement (clés sécurisées)
TAPIT_API_KEY = os.environ.get('TAPIT_API_KEY')
TAPIT_LINK_ID = os.environ.get('TAPIT_LINK_ID')  # L'ID de ton lien Tap.it
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def get_tapit_stats():
    """Récupère les statistiques depuis l'API Tap.it"""
    
    # URL de l'API Tap.it (à ajuster selon leur documentation)
    # Note: Ceci est un exemple, l'URL exacte dépend de la doc Tap.it
    url = f"https://api.tap.it/v1/links/{TAPIT_LINK_ID}/stats"
    
    headers = {
        "Authorization": f"Bearer {TAPIT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Extraction du nombre de clics (à ajuster selon la structure de réponse)
        clicks = data.get('clicks', 0)
        return clicks
    
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des stats: {e}")
        return None

def send_to_discord(clicks):
    """Envoie les statistiques sur Discord via webhook"""
    
    if clicks is None:
        message = "❌ Erreur lors de la récupération des statistiques Tap.it"
    else:
        today = datetime.now().strftime("%d/%m/%Y")
        message = f"📊 **Statistiques Tap.it - {today}**\n\n👆 **Clics totaux:** {clicks:,}"
    
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
    if not all([TAPIT_API_KEY, TAPIT_LINK_ID, DISCORD_WEBHOOK_URL]):
        print("❌ Variables d'environnement manquantes!")
        return
    
    # Récupération et envoi des stats
    clicks = get_tapit_stats()
    send_to_discord(clicks)

if __name__ == "__main__":
    main()
```
