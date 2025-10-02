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

def get_planned_events(date_obj):
    """Récupère les événements programmés"""
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
    """Journées mondiales"""
    journees = {
        (1, 1): "Journée mondiale de la Paix",
        (4, 1): "Journée mondiale du braille",
        (4, 2): "Journée mondiale contre le cancer",
        (14, 2): "Saint-Valentin",
        (8, 3): "Journée internationale des droits des femmes",
        (20, 3): "Journée internationale de la Francophonie",
        (22, 3): "Journée mondiale de l'eau",
        (7, 4): "Journée mondiale de la santé",
        (22, 4): "Jour de la Terre",
        (1, 5): "Fête du Travail",
        (8, 5): "Fin de la Seconde Guerre mondiale en Europe",
        (1, 6): "Journée mondiale de l'enfance",
        (5, 6): "Journée mondiale de l'environnement",
        (21, 6): "Fête de la musique",
        (14, 7): "Fête nationale française",
        (8, 9): "Journée internationale de l'alphabétisation",
        (21, 9): "Journée internationale de la paix",
        (1, 10): "Journée internationale des personnes âgées",
        (5, 10): "Journée mondiale des enseignants",
        (16, 10): "Journée mondiale de l'alimentation",
        (31, 10): "Halloween",
        (1, 11): "Toussaint",
        (11, 11): "Armistice de 1918",
        (20, 11): "Journée internationale des droits de l'enfant",
        (25, 12): "Noël",
        (31, 12): "Saint-Sylvestre"
    }
    return journees.get((day, month), None)

def get_historical_event(day, month):
    """Événements historiques"""
    events = {
        (1, 1): "1999 : Passage à l'euro dans 11 pays européens",
        (14, 2): "1876 : Alexander Graham Bell dépose un brevet pour le téléphone",
        (8, 3): "1910 : Premier vol d'une femme pilote, Raymonde de Laroche",
        (15, 3): "44 av. J.-C. : Assassinat de Jules César",
        (1, 4): "1976 : Création d'Apple Computer",
        (12, 4): "1961 : Youri Gagarine, premier homme dans l'espace",
        (15, 4): "1912 : Naufrage du Titanic",
        (1, 5): "1886 : Début de la grève de Haymarket à Chicago",
        (8, 5): "1945 : Fin de la Seconde Guerre mondiale en Europe",
        (6, 6): "1944 : Débarquement de Normandie",
        (14, 7): "1789 : Prise de la Bastille",
        (20, 7): "1969 : Neil Armstrong marche sur la Lune",
        (6, 8): "1945 : Bombardement atomique d'Hiroshima",
        (11, 9): "2001 : Attentats du World Trade Center",
        (1, 10): "1949 : Proclamation de la République populaire de Chine",
        (3, 10): "1990 : Réunification allemande",
        (12, 10): "1492 : Christophe Colomb découvre l'Amérique",
        (9, 11): "1989 : Chute du mur de Berlin",
        (11, 11): "1918 : Armistice de la Première Guerre mondiale",
        (22, 11): "1963 : Assassinat de John F. Kennedy",
        (7, 12): "1941 : Attaque de Pearl Harbor",
        (10, 12): "1948 : Adoption de la Déclaration universelle des droits de l'homme"
    }
    return events.get((day, month), None)

def get_weather_forecast():
    """Récupère météo via Open-Meteo"""
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
    except:
        return None

def extract_tomorrow_forecast(data):
    """Extrait prévisions 8h, 12h, 16h, 20h"""
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
                    'precip': precip[i],
                    'weather_code': weather_codes[i],
                    'wind': wind_speeds[i]
                }
    
    return forecasts

def get_weather_emoji(code):
    """Emoji météo"""
    emojis = {
        0: "☀️", 1: "🌤️", 2: "🌤️", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌦️", 55: "🌦️",
        61: "🌧️", 63: "🌧️", 65: "🌧️",
        71: "❄️", 73: "❄️", 75: "❄️",
        80: "🌧️", 81: "🌧️", 82: "🌧️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return emojis.get(code, "🌡️")

def get_weather_description(code):
    """Description météo"""
    descriptions = {
        0: "Ciel dégagé", 1: "Peu nuageux", 2: "Partiellement nuageux", 3: "Nuageux",
        45: "Brouillard", 51: "Bruine légère", 53: "Bruine modérée",
        61: "Pluie légère", 63: "Pluie modérée", 65: "Pluie forte",
        71: "Neige légère", 73: "Neige modérée", 75: "Neige forte",
        80: "Averses légères", 81: "Averses modérées", 95: "Orage"
    }
    return descriptions.get(code, "Conditions variables")

def format_weather_bulletin(tomorrow_info, forecasts):
    """Formate le bulletin"""
    if not forecasts:
        return None
    
    day = tomorrow_info['day_num']
    month = tomorrow_info['month']
    date_obj = tomorrow_info['date_obj']
    
    planned = get_planned_events(date_obj)
    journee = get_journee_mondiale(day, month)
    event = get_historical_event(day, month)
    
    description = f"📅 **{tomorrow_info['formatted'].upper()}**\n"
    
    if planned:
        for p in planned:
            emoji_map = {'greve': '🚨', 'ferie': '🎉', 'exam': '📝', 'autre': 'ℹ️'}
            emoji = emoji_map.get(p.get('type', 'autre'), 'ℹ️')
            description += f"\n{emoji} **{p['title']}**\n{p['description']}\n"
    
    if journee:
        description += f"\n🎉 **{journee}**\n"
    
    if event:
        description += f"\n📖 **Le saviez-vous ?**\n{event}\n"
    
    description += "\n━━━━━━━━━━━━━━━━━━━━━━\n🌤️ **PRÉVISIONS MÉTÉO - LE HAVRE**\n━━━━━━━━━━━━━━━━━━━━━━\n"
    
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
    
    avg_temp = sum(f['temp'] for f in forecasts.values()) / len(forecasts)
    max_precip = max(f['precip'] for f in forecasts.values())
    
    if max_precip > 60:
        conseil = "☔ N'oubliez pas votre parapluie !"
    elif avg_temp < 10:
        conseil = "🧥 Pensez à vous couvrir !"
    elif avg_temp > 25:
        conseil = "😎 Profitez du beau temps !"
    else:
        conseil = "👌 Temps agréable prévu !"
    
    description += f"\n💡 **Conseil du jour :** {conseil}"
    return description.strip()

def send_bulletin():
    """Envoie le bulletin"""
    tomorrow = get_tomorrow_date()
    forecasts = get_weather_forecast()
    
    if not forecasts:
        return False
    
    bulletin = format_weather_bulletin(tomorrow, forecasts)
    
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
        requests.post(WEBHOOK_URL, json=payload, timeout=15).raise_for_status()
        return True
    except:
        return False

def main():
    print("BULLETIN MÉTÉO QUOTIDIEN")
    print(f"Exécution: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    if send_bulletin():
        print("✅ Bulletin envoyé")
    else:
        print("❌ Échec")

if __name__ == "__main__":
    main()
