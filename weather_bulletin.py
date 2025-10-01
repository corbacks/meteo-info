#!/usr/bin/env python3
"""
Bulletin météo quotidien à 20h avec prévisions du lendemain
"""
import os
import requests
import json
from datetime import datetime, timedelta

WEBHOOK_URL = "https://discord.com/api/webhooks/1423015970523320320/NEeoliSALJV-OORt_cDezxiqeX6fugRUSUqurjLPIwbvawBrbb6wAWHIVHBo7S1YPjSX"
ROLE_ID = "1423013715594444821"

# Coordonnées Le Havre
LATITUDE = 49.4944
LONGITUDE = 0.1079

def get_tomorrow_date():
    """Obtient la date de demain"""
    try:
        import pytz
        paris_tz = pytz.timezone("Europe/Paris")
        tomorrow = datetime.now(paris_tz) + timedelta(days=1)
    except ImportError:
        tomorrow = datetime.now() + timedelta(days=1)
    
    days_fr = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    months_fr = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    
    day_name = days_fr[tomorrow.weekday()]
    month_name = months_fr[tomorrow.month - 1]
    
    return {
        'formatted': f"{day_name} {tomorrow.day} {month_name} {tomorrow.year}",
        'day_name': day_name.capitalize(),
        'day_num': tomorrow.day,
        'month': tomorrow.month,
        'month_name': month_name,
        'year': tomorrow.year,
        'date_obj': tomorrow
    }

def get_weather_forecast():
    """Récupère les prévisions météo via Open-Meteo (gratuit, pas de clé API)"""
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': LATITUDE,
        'longitude': LONGITUDE,
        'hourly': 'temperature_2m,precipitation_probability,weathercode,windspeed_10m',
        'timezone': 'Europe/Paris',
        'forecast_days': 2
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Extraire les prévisions de demain
        tomorrow_forecast = extract_tomorrow_forecast(data)
        return tomorrow_forecast
        
    except Exception as e:
        print(f"Erreur météo: {e}")
        return None

def extract_tomorrow_forecast(data):
    """Extrait les prévisions pour 8h, 12h, 16h, 20h de demain"""
    
    hourly = data.get('hourly', {})
    times = hourly.get('time', [])
    temps = hourly.get('temperature_2m', [])
    precip = hourly.get('precipitation_probability', [])
    weather_codes = hourly.get('weathercode', [])
    wind_speeds = hourly.get('windspeed_10m', [])
    
    # Trouver demain
    tomorrow = datetime.now() + timedelta(days=1)
    target_date = tomorrow.strftime('%Y-%m-%d')
    
    forecasts = {}
    target_hours = [8, 12, 16, 20]
    
    for i, time_str in enumerate(times):
        if target_date in time_str:
            hour = int(time_str.split('T')[1].split(':')[0])
            if hour in target_hours:
                forecasts[hour] = {
                    'temp': temps[i],
                    'precip': precip[i],
                    'weather_code': weather_codes[i],
                    'wind': wind_speeds[i]
                }
    
    return forecasts

def get_weather_emoji(weather_code):
    """Convertit le code météo en emoji"""
    # Codes WMO
    if weather_code == 0:
        return "☀️"  # Ciel dégagé
    elif weather_code in [1, 2]:
        return "🌤️"  # Peu nuageux
    elif weather_code == 3:
        return "☁️"  # Nuageux
    elif weather_code in [45, 48]:
        return "🌫️"  # Brouillard
    elif weather_code in [51, 53, 55]:
        return "🌦️"  # Bruine
    elif weather_code in [61, 63, 65]:
        return "🌧️"  # Pluie
    elif weather_code in [71, 73, 75]:
        return "❄️"  # Neige
    elif weather_code in [80, 81, 82]:
        return "🌧️"  # Averses
    elif weather_code in [95, 96, 99]:
        return "⛈️"  # Orage
    else:
        return "🌡️"

def get_weather_description(weather_code):
    """Description textuelle de la météo"""
    descriptions = {
        0: "Ciel dégagé",
        1: "Peu nuageux",
        2: "Partiellement nuageux",
        3: "Nuageux",
        45: "Brouillard",
        48: "Brouillard givrant",
        51: "Bruine légère",
        53: "Bruine modérée",
        55: "Bruine dense",
        61: "Pluie légère",
        63: "Pluie modérée",
        65: "Pluie forte",
        71: "Neige légère",
        73: "Neige modérée",
        75: "Neige forte",
        80: "Averses légères",
        81: "Averses modérées",
        82: "Averses violentes",
        95: "Orage",
        96: "Orage avec grêle légère",
        99: "Orage avec grêle forte"
    }
    return descriptions.get(weather_code, "Conditions variables")

def get_planned_events(date_obj):
    """Récupère les événements programmés pour demain"""
    try:
        from pathlib import Path
        import json
        
        events_file = Path("planned_events.json")
        if not events_file.exists():
            return []
        
        with open(events_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        target_date = date_obj.strftime('%Y-%m-%d')
        planned = []
        
        for event in data.get('events', []):
            if event.get('date') == target_date:
                planned.append(event)
        
        return planned
    except Exception as e:
        print(f"Erreur lecture événements: {e}")
        return []
    """Retourne la journée mondiale du jour"""
    journees = {
        (1, 1): "Journée mondiale de la Paix",
        (4, 1): "Journée mondiale du braille",
        (24, 1): "Journée internationale de l'éducation",
        (27, 1): "Journée de la mémoire de l'Holocauste",
        (4, 2): "Journée mondiale contre le cancer",
        (11, 2): "Journée internationale des femmes et des filles de science",
        (13, 2): "Journée mondiale de la radio",
        (14, 2): "Saint-Valentin",
        (20, 2): "Journée mondiale de la justice sociale",
        (21, 2): "Journée internationale de la langue maternelle",
        (8, 3): "Journée internationale des droits des femmes",
        (20, 3): "Journée internationale de la Francophonie",
        (21, 3): "Journée internationale des forêts",
        (22, 3): "Journée mondiale de l'eau",
        (2, 4): "Journée mondiale de sensibilisation à l'autisme",
        (7, 4): "Journée mondiale de la santé",
        (22, 4): "Jour de la Terre",
        (23, 4): "Journée mondiale du livre",
        (1, 5): "Fête du Travail",
        (3, 5): "Journée mondiale de la liberté de la presse",
        (8, 5): "Fin de la Seconde Guerre mondiale en Europe",
        (17, 5): "Journée mondiale des télécommunications",
        (21, 5): "Journée mondiale de la diversité culturelle",
        (1, 6): "Journée mondiale de l'enfance",
        (5, 6): "Journée mondiale de l'environnement",
        (8, 6): "Journée mondiale des océans",
        (21, 6): "Fête de la musique",
        (14, 7): "Fête nationale française",
        (30, 7): "Journée mondiale de l'amitié",
        (9, 8): "Journée internationale des peuples autochtones",
        (12, 8): "Journée internationale de la jeunesse",
        (19, 8): "Journée mondiale de la photographie",
        (8, 9): "Journée internationale de l'alphabétisation",
        (21, 9): "Journée internationale de la paix",
        (27, 9): "Journée mondiale du tourisme",
        (1, 10): "Journée internationale des personnes âgées",
        (2, 10): "Journée internationale de la non-violence",
        (5, 10): "Journée mondiale des enseignants",
        (10, 10): "Journée mondiale de la santé mentale",
        (16, 10): "Journée mondiale de l'alimentation",
        (24, 10): "Journée des Nations Unies",
        (31, 10): "Halloween",
        (1, 11): "Toussaint",
        (11, 11): "Armistice de 1918",
        (16, 11): "Journée internationale de la tolérance",
        (19, 11): "Journée mondiale des toilettes",
        (20, 11): "Journée internationale des droits de l'enfant",
        (25, 11): "Journée internationale pour l'élimination de la violence à l'égard des femmes",
        (1, 12): "Journée mondiale de lutte contre le SIDA",
        (3, 12): "Journée internationale des personnes handicapées",
        (10, 12): "Journée des droits de l'homme",
        (25, 12): "Noël",
        (31, 12): "Saint-Sylvestre"
    }
    return journees.get((day, month), None)

def get_historical_event(day, month):
    """Retourne un événement historique pour cette date"""
    events = {
        (1, 1): "1999 : Passage à l'euro dans 11 pays européens",
        (2, 1): "1959 : Luna 1, premier objet à quitter l'orbite terrestre",
        (3, 1): "1977 : Apple Computer devient une société",
        (4, 1): "2010 : Inauguration du Burj Khalifa, plus haute tour du monde",
        (5, 1): "1968 : Début du Printemps de Prague",
        (14, 2): "1876 : Alexander Graham Bell dépose un brevet pour le téléphone",
        (20, 2): "1947 : Lord Mountbatten devient vice-roi des Indes",
        (21, 2): "1848 : Publication du Manifeste du Parti communiste",
        (8, 3): "1910 : Premier vol d'une femme pilote, Raymonde de Laroche",
        (15, 3): "44 av. J.-C. : Assassinat de Jules César",
        (20, 3): "1852 : Publication de 'La Case de l'oncle Tom'",
        (21, 3): "1960 : Massacre de Sharpeville en Afrique du Sud",
        (1, 4): "1976 : Création d'Apple Computer par Steve Jobs et Steve Wozniak",
        (4, 4): "1968 : Assassinat de Martin Luther King Jr.",
        (12, 4): "1961 : Youri Gagarine devient le premier homme dans l'espace",
        (15, 4): "1912 : Naufrage du Titanic",
        (22, 4): "1970 : Premier Jour de la Terre",
        (1, 5): "1886 : Début de la grève de Haymarket à Chicago",
        (8, 5): "1945 : Fin de la Seconde Guerre mondiale en Europe",
        (14, 5): "1796 : Edward Jenner teste le premier vaccin contre la variole",
        (21, 5): "1927 : Charles Lindbergh atterrit à Paris après sa traversée de l'Atlantique",
        (4, 6): "1989 : Massacre de la place Tian'anmen",
        (6, 6): "1944 : Débarquement de Normandie",
        (18, 6): "1815 : Bataille de Waterloo",
        (28, 6): "1914 : Assassinat de l'archiduc François-Ferdinand à Sarajevo",
        (4, 7): "1776 : Déclaration d'indépendance des États-Unis",
        (14, 7): "1789 : Prise de la Bastille",
        (20, 7): "1969 : Neil Armstrong marche sur la Lune",
        (21, 7): "1969 : Premier pas de l'Homme sur la Lune",
        (6, 8): "1945 : Bombardement atomique d'Hiroshima",
        (9, 8): "1945 : Bombardement atomique de Nagasaki",
        (15, 8): "1947 : Indépendance de l'Inde",
        (28, 8): "1963 : Discours 'I Have a Dream' de Martin Luther King",
        (1, 9): "1939 : Début de la Seconde Guerre mondiale",
        (11, 9): "2001 : Attentats du World Trade Center",
        (21, 9): "1792 : Abolition de la monarchie en France",
        (28, 9): "1958 : Référendum sur la Constitution de la Ve République",
        (1, 10): "1949 : Proclamation de la République populaire de Chine",
        (2, 10): "1187 : Saladin reprend Jérusalem aux Croisés",
        (3, 10): "1990 : Réunification allemande",
        (4, 10): "1957 : Lancement de Spoutnik 1, premier satellite artificiel",
        (5, 10): "1962 : Sortie du premier single des Beatles",
        (12, 10): "1492 : Christophe Colomb découvre l'Amérique",
        (24, 10): "1929 : Jeudi noir, début de la Grande Dépression",
        (29, 10): "1929 : Krach boursier de Wall Street",
        (9, 11): "1989 : Chute du mur de Berlin",
        (11, 11): "1918 : Armistice de la Première Guerre mondiale",
        (22, 11): "1963 : Assassinat de John F. Kennedy",
        (26, 11): "1922 : Découverte du tombeau de Toutânkhamon",
        (1, 12): "1955 : Rosa Parks refuse de céder sa place dans un bus",
        (7, 12): "1941 : Attaque de Pearl Harbor",
        (10, 12): "1948 : Adoption de la Déclaration universelle des droits de l'homme",
        (17, 12): "1903 : Premier vol motorisé des frères Wright",
        (25, 12): "800 : Couronnement de Charlemagne"
    }
    return events.get((day, month), None)

def format_weather_bulletin(tomorrow_info, forecasts):
    """Formate le bulletin météo avec données complètes"""
    
    if not forecasts:
        return None
    
    day = tomorrow_info['day_num']
    month = tomorrow_info['month']
    date_obj = tomorrow_info['date_obj']
    
    # Récupérer les infos du jour
    journee = get_journee_mondiale(day, month)
    event = get_historical_event(day, month)
    planned = get_planned_events(date_obj)
    
    # En-tête
    description = f"""
📅 **{tomorrow_info['formatted'].upper()}**
"""
    
    # Événements programmés (prioritaires)
    if planned:
        for p_event in planned:
            emoji_map = {
                'greve': '🚨',
                'ferie': '🎉',
                'exam': '📝',
                'autre': 'ℹ️'
            }
            emoji = emoji_map.get(p_event.get('type', 'autre'), 'ℹ️')
            description += f"\n{emoji} **{p_event['title']}**\n{p_event['description']}\n"
    
    # Journée mondiale si disponible
    if journee:
        description += f"\n🎉 **{journee}**\n"
    
    # Événement historique si disponible
    if event:
        description += f"\n📖 **Le saviez-vous ?**\n{event}\n"
    
    description += """
━━━━━━━━━━━━━━━━━━━━━━
🌤️ **PRÉVISIONS MÉTÉO - LE HAVRE**
━━━━━━━━━━━━━━━━━━━━━━
"""

    # Prévisions par tranche horaire
    hours_labels = {
        8: "🌅 **MATIN (8h)**",
        12: "☀️ **MIDI (12h)**",
        16: "🌆 **APRÈS-MIDI (16h)**",
        20: "🌙 **SOIRÉE (20h)**"
    }
    
    for hour in [8, 12, 16, 20]:
        if hour in forecasts:
            f = forecasts[hour]
            emoji = get_weather_emoji(f['weather_code'])
            desc = get_weather_description(f['weather_code'])
            
            description += f"""
{hours_labels[hour]}
{emoji} {desc}
🌡️ Température : **{f['temp']:.1f}°C**
💧 Précipitations : {f['precip']}%
💨 Vent : {f['wind']:.0f} km/h

"""
    
    # Conseil basé sur météo
    avg_temp = sum(f['temp'] for f in forecasts.values()) / len(forecasts)
    max_precip = max(f['precip'] for f in forecasts.values())
    
    if max_precip > 60:
        conseil = "☔ N'oubliez pas votre parapluie !"
    elif avg_temp < 10:
        conseil = "🧥 Pensez à vous couvrir, il fera frais !"
    elif avg_temp > 25:
        conseil = "😎 Profitez du beau temps !"
    else:
        conseil = "👌 Temps agréable prévu !"
    
    description += f"💡 **Conseil du jour :** {conseil}"
    
    return description.strip()

def send_bulletin():
    """Envoie le bulletin sur Discord"""
    
    print("Préparation du bulletin météo...")
    
    tomorrow = get_tomorrow_date()
    print(f"Date demain: {tomorrow['formatted']}")
    
    forecasts = get_weather_forecast()
    
    if not forecasts:
        print("Impossible de récupérer les prévisions météo")
        return False
    
    print(f"Prévisions récupérées: {len(forecasts)} créneaux horaires")
    
    bulletin = format_weather_bulletin(tomorrow, forecasts)
    
    if not bulletin:
        print("Erreur lors du formatage du bulletin")
        return False
    
    # Créer l'embed
    embed = {
        "title": "📰 Bulletin Quotidien",
        "description": bulletin,
        "color": 0x3498db,  # Bleu
        "footer": {
            "text": "Bulletin automatique • Prévisions Open-Meteo"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # Message avec mention
    payload = {
        "username": "📰 Bulletin Quotidien",
        "content": f"<@&{ROLE_ID}>",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=15)
        response.raise_for_status()
        print(f"Bulletin envoyé ! (status: {response.status_code})")
        return True
    except Exception as e:
        print(f"Erreur envoi Discord: {e}")
        return False

def main():
    print("="*60)
    print("BULLETIN MÉTÉO QUOTIDIEN")
    print(f"Exécution: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*60)
    
    success = send_bulletin()
    
    if success:
        print("Bulletin envoyé avec succès !")
    else:
        print("Échec de l'envoi du bulletin")

if __name__ == "__main__":
    main()
