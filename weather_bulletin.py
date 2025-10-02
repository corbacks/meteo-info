#!/usr/bin/env python3
"""
Bulletin météo quotidien à 20h avec prévisions du lendemain
Source: Open-Meteo API (données fiables)
"""
import requests
import json
from datetime import datetime, timedelta

WEBHOOK_URL = "https://discord.com/api/webhooks/1423015970523320320/NEeoliSALJV-OORt_cDezxiqeX6fugRUSUqurjLPIwbvawBrbb6wAWHIVHBo7S1YPjSX"
ROLE_ID = "1423013715594444821"
LATITUDE = 49.4944
LONGITUDE = 0.1079

def get_tomorrow_date():
    """Obtient la date de demain en heure de Paris"""
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

def get_planned_events(date_obj):
    """Récupère les événements programmés depuis planned_events.json"""
    try:
        from pathlib import Path
        
        events_file = Path("planned_events.json")
        if not events_file.exists():
            return []
        
        with open(events_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        target_date = date_obj.strftime('%Y-%m-%d')
        return [e for e in data.get('events', []) if e.get('date') == target_date]
    except:
        return []

def get_journee_mondiale(day, month):
    """Journées mondiales importantes"""
    journees = {
        # --- JANVIER ---
        (1, 1): "Journée mondiale de la Paix / Nouvel An",
        (4, 1): "Journée mondiale du braille",
        (6, 1): "Épiphanie",
        (27, 1): "Journée internationale de commémoration des victimes de l'Holocauste",

        # --- FÉVRIER ---
        (4, 2): "Journée mondiale contre le cancer",
        (14, 2): "Saint-Valentin",
        (20, 2): "Journée mondiale de la justice sociale",
        (21, 2): "Journée internationale de la langue maternelle",

        # --- MARS ---
        (8, 3): "Journée internationale des droits des femmes",
        (20, 3): "Journée internationale de la Francophonie",
        (21, 3): "Journée internationale pour l'élimination de la discrimination raciale",
        (22, 3): "Journée mondiale de l'eau",
        (27, 3): "Journée mondiale du théâtre",

        # --- AVRIL ---
        (7, 4): "Journée mondiale de la santé",
        (22, 4): "Jour de la Terre",
        (23, 4): "Journée mondiale du livre et du droit d'auteur",
        (25, 4): "Journée mondiale de lutte contre le paludisme",
        (26, 4): "Journée mondiale de la propriété intellectuelle"

        # --- MAI ---
        (1, 5): "Fête du Travail",
        (3, 5): "Journée mondiale de la liberté de la presse",
        (8, 5): "Journée mondiale de la Croix-Rouge",
        (15, 5): "Journée internationale des familles",
        (17, 5): "Journée mondiale de lutte contre l'homophobie",
        (22, 5): "Journée mondiale de la biodiversité",
        (31, 5): "Journée mondiale sans tabac",

        # --- JUIN ---
        (1, 6): "Journée mondiale de l'enfance",
        (5, 6): "Journée mondiale de l'environnement",
        (8, 6): "Journée mondiale des océans",
        (14, 6): "Journée mondiale du donneur de sang",
        (20, 6): "Journée mondiale des réfugiés",
        (21, 6): "Fête de la musique",
        (26, 6): "Journée internationale contre l'abus et le trafic de drogues",

        # --- JUILLET ---
        (11, 7): "Journée mondiale de la population",
        (14, 7): "Fête nationale française",
        (18, 7): "Journée Nelson Mandela",
        (30, 7): "Journée internationale de l'amitié",

        # --- AOÛT ---
        (9, 8): "Journée internationale des peuples autochtones",
        (12, 8): "Journée internationale de la jeunesse",
        (19, 8): "Journée mondiale de l'aide humanitaire",
        (23, 8): "Journée internationale du souvenir de la traite négrière et de son abolition",
        (29, 8): "Journée internationale contre les essais nucléaires"

        # --- SEPTEMBRE ---
        (8, 9): "Journée internationale de l'alphabétisation",
        (15, 9): "Journée internationale de la démocratie",
        (16, 9): "Journée internationale de la protection de la couche d'ozone",
        (21, 9): "Journée internationale de la paix",
        (27, 9): "Journée mondiale du tourisme",
        (29, 9): "Journée mondiale du cœur",

        # --- OCTOBRE ---
        (1, 10): "Journée internationale des personnes âgées",
        (4, 10): "Journée mondiale des animaux",
        (5, 10): "Journée mondiale des enseignants",
        (10, 10): "Journée mondiale de la santé mentale",
        (16, 10): "Journée mondiale de l’alimentation",
        (17, 10): "Journée internationale pour l’élimination de la pauvreté",
        (24, 10): "Journée des Nations Unies",
        (31, 10): "Halloween",

        # --- NOVEMBRE ---
        (1, 11): "Toussaint",
        (14, 11): "Journée mondiale du diabète",
        (16, 11): "Journée internationale de la tolérance",
        (20, 11): "Journée internationale des droits de l'enfant",
        (21, 11): "Journée mondiale de la télévision",
        (25, 11): "Journée internationale pour l’élimination de la violence à l’égard des femmes",

        # --- DÉCEMBRE ---
        (1, 12): "Journée mondiale de lutte contre le sida",
        (3, 12): "Journée internationale des personnes handicapées",
        (10, 12): "Journée des droits de l'homme",
        (25, 12): "Noël",
        (31, 12): "Saint-Sylvestre"
    }
    return journees.get((day, month), None)

def get_historical_event(day, month):
    """Événements historiques marquants"""
    events = {
        # --- JANVIER ---
        (1, 1): "1999 : Passage à l'euro dans 11 pays européens",
        (7, 1): "1610 : Galileo découvre les lunes de Jupiter",
        (24, 1): "1848 : Découverte de l'or en Californie",

        # --- FÉVRIER ---
        (14, 2): "1876 : Alexander Graham Bell dépose un brevet pour le téléphone",
        (21, 2): "1965 : Malcolm X est assassiné",
        (27, 2): "1933 : Première diffusion d'un film au cinéma parlant aux États-Unis",

        # --- MARS ---
        (8, 3): "1910 : Premier vol d'une femme pilote, Raymonde de Laroche",
        (15, 3): "44 av. J.-C. : Assassinat de Jules César",
        (20, 3): "2003 : Début de la guerre en Irak",
        (22, 3): "1963 : Martin Luther King prononce 'I Have a Dream' à Birmingham",

        # --- AVRIL ---
        (1, 4): "1976 : Création d'Apple Computer",
        (12, 4): "1961 : Youri Gagarine, premier homme dans l'espace",
        (15, 4): "1912 : Naufrage du Titanic",
        (25, 4): "1953 : Découverte de la structure de l'ADN",

        # --- MAI ---
        (1, 5): "1886 : Début de la grève de Haymarket à Chicago",
        (8, 5): "1945 : Fin de la Seconde Guerre mondiale en Europe",
        (17, 5): "1954 : Arrêt Brown v. Board of Education aux États-Unis",
        (29, 5): "1953 : Edmund Hillary et Tenzing Norgay atteignent le sommet de l'Everest",

        # --- JUIN ---
        (6, 6): "1944 : Débarquement de Normandie",
        (16, 6): "1963 : Valentina Terechkova devient la première femme dans l'espace",
        (20, 6): "1789 : Serment du Jeu de Paume",
        (26, 6): "1945 : Charte des Nations Unies signée",

        # --- JUILLET ---
        (14, 7): "1789 : Prise de la Bastille",
        (20, 7): "1969 : Neil Armstrong marche sur la Lune",
        (25, 7): "1978 : Naissance de Louise Brown, premier bébé-éprouvette",

        # --- AOÛT ---
        (6, 8): "1945 : Bombardement atomique d'Hiroshima",
        (9, 8): "1945 : Bombardement atomique de Nagasaki",
        (15, 8): "1947 : Indépendance de l'Inde",
        (30, 8): "1963 : Martin Luther King prononce 'I Have a Dream'",

        # --- SEPTEMBRE ---
        (11, 9): "2001 : Attentats du World Trade Center",
        (8, 9): "1966 : Première émission de Star Trek",
        (21, 9): "1937 : Début du vol autour du monde de Wiley Post",

        # --- OCTOBRE ---
        (1, 10): "1949 : Proclamation de la République populaire de Chine",
        (3, 10): "1990 : Réunification allemande",
        (12, 10): "1492 : Christophe Colomb découvre l'Amérique",
        (24, 10): "1929 : Krach boursier de Wall Street",

        # --- NOVEMBRE ---
        (9, 11): "1989 : Chute du mur de Berlin",
        (11, 11): "1918 : Armistice de la Première Guerre mondiale",
        (22, 11): "1963 : Assassinat de John F. Kennedy",
        (20, 11): "1945 : Fondation de l'UNESCO",

        # --- DÉCEMBRE ---
        (7, 12): "1941 : Attaque de Pearl Harbor",
        (10, 12): "1948 : Adoption de la Déclaration universelle des droits de l'homme",
        (25, 12): "800 : Couronnement de Charlemagne",
        (31, 12): "1999 : Passage au nouvel an 2000"

    }
    return events.get((day, month), None)

def get_weather_forecast():
    """Récupère météo via Open-Meteo (API fiable et gratuite)"""
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
        return extract_tomorrow_forecast(data)
    except Exception as e:
        print(f"⚠️ Erreur météo: {e}")
        return None

def extract_tomorrow_forecast(data):
    """Extrait prévisions pour 8h, 12h, 16h, 20h de demain"""
    hourly = data.get('hourly', {})
    times = hourly.get('time', [])
    temps = hourly.get('temperature_2m', [])
    precip = hourly.get('precipitation_probability', [])
    weather_codes = hourly.get('weathercode', [])
    wind_speeds = hourly.get('windspeed_10m', [])
    
    tomorrow = datetime.now() + timedelta(days=1)
    target_date = tomorrow.strftime('%Y-%m-%d')
    
    forecasts = {}
    for i, time_str in enumerate(times):
        if target_date in time_str:
            hour = int(time_str.split('T')[1].split(':')[0])
            if hour in [8, 12, 16, 20]:
                forecasts[hour] = {
                    'temp': temps[i],
                    'precip': precip[i] if i < len(precip) else 0,
                    'weather_code': weather_codes[i],
                    'wind': wind_speeds[i]
                }
    
    return forecasts

def get_weather_emoji(code):
    """Emoji météo selon code WMO"""
    emojis = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌦️", 55: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "🌧️",
        71: "❄️", 73: "❄️", 75: "❄️",
        80: "🌦️", 81: "🌧️", 82: "🌧️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return emojis.get(code, "🌡️")

def get_weather_description(code):
    """Description météo en français"""
    descriptions = {
        0: "Ciel dégagé", 1: "Peu nuageux", 2: "Partiellement nuageux", 3: "Nuageux",
        45: "Brouillard", 48: "Brouillard givrant",
        51: "Bruine légère", 53: "Bruine modérée", 55: "Bruine dense",
        61: "Pluie légère", 63: "Pluie modérée", 65: "Pluie forte",
        71: "Neige légère", 73: "Neige modérée", 75: "Neige forte",
        80: "Averses légères", 81: "Averses modérées", 82: "Averses fortes",
        95: "Orage", 96: "Orage avec grêle", 99: "Orage violent"
    }
    return descriptions.get(code, "Conditions variables")

def format_weather_bulletin(tomorrow_info, forecasts):
    """Formate le bulletin complet"""
    if not forecasts:
        return None
    
    day = tomorrow_info['day_num']
    month = tomorrow_info['month']
    date_obj = tomorrow_info['date_obj']
    
    planned = get_planned_events(date_obj)
    journee = get_journee_mondiale(day, month)
    event = get_historical_event(day, month)
    
    description = f"📅 **{tomorrow_info['formatted'].upper()}**\n"
    
    # Événements programmés (grèves, jours fériés...)
    if planned:
        for p in planned:
            emoji_map = {
                'greve': '🚨',
                'ferie': '🎉',
                'transport': '🚌',
                'autre': 'ℹ️'
            }
            emoji = emoji_map.get(p.get('type', 'autre'), 'ℹ️')
            desc_text = p.get('description', '')[:150]
            description += f"\n{emoji} **{p['title']}**\n{desc_text}\n"
    
    # Journée mondiale
    if journee:
        description += f"\n🎉 **{journee}**\n"
    
    # Événement historique
    if event:
        description += f"\n📖 **Le saviez-vous ?**\n{event}\n"
    
    description += "\n━━━━━━━━━━━━━━━━━━━━━\n🌤️ **PRÉVISIONS MÉTÉO - LE HAVRE**\n━━━━━━━━━━━━━━━━━━━━━\n"
    
    hours_labels = {
        8: "🌅 **MATIN (8h)**",
        12: "☀️ **MIDI (12h)**",
        16: "🌆 **APRÈS-MIDI (16h)**",
        20: "🌙 **SOIRÉE (20h)**"
    }
    
    for hour in [8, 12, 16, 20]:
        if hour in forecasts:
            f = forecasts[hour]
            description += f"\n{hours_labels[hour]}\n"
            description += f"{get_weather_emoji(f['weather_code'])} {get_weather_description(f['weather_code'])}\n"
            description += f"🌡️ Température : **{f['temp']:.1f}°C**\n"
            description += f"💧 Précipitations : {f['precip']}%\n"
            description += f"💨 Vent : {f['wind']:.0f} km/h\n"
    
    # Conseil du jour
    avg_temp = sum(f['temp'] for f in forecasts.values()) / len(forecasts)
    max_precip = max(f['precip'] for f in forecasts.values())
    
    if max_precip > 60:
        conseil = "☂️ N'oubliez pas votre parapluie !"
    elif avg_temp < 10:
        conseil = "🧥 Pensez à vous couvrir !"
    elif avg_temp > 25:
        conseil = "😎 Profitez du beau temps !"
    else:
        conseil = "👌 Temps agréable prévu !"
    
    description += f"\n💡 **Conseil du jour :** {conseil}"
    return description.strip()

def send_bulletin():
    """Envoie le bulletin sur Discord"""
    tomorrow = get_tomorrow_date()
    forecasts = get_weather_forecast()
    
    if not forecasts:
        print("❌ Impossible de récupérer la météo")
        return False
    
    bulletin = format_weather_bulletin(tomorrow, forecasts)
    
    if not bulletin:
        print("❌ Impossible de formater le bulletin")
        return False
    
    embed = {
        "title": "📰 Bulletin Quotidien",
        "description": bulletin,
        "color": 0x3498db,
        "footer": {"text": "Bulletin automatique • Open-Meteo"},
        "timestamp": datetime.now().isoformat()
    }
    
    payload = {
        "username": "📰 Bulletin Quotidien",
        "content": f"<@&{ROLE_ID}>",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=15)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Erreur Discord: {e}")
        return False

def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  BULLETIN MÉTÉO QUOTIDIEN")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    if send_bulletin():
        print("✅ Bulletin envoyé avec succès")
    else:
        print("❌ Échec de l'envoi")

if __name__ == "__main__":
    main()
