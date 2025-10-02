#!/usr/bin/env python3
"""
Bulletin météo quotidien à 20h avec prévisions du lendemain
Version améliorée avec style moderne et emojis
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
        'date_obj': tomorrow,
        'is_weekend': tomorrow.weekday() >= 5
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
        (1, 1): "Journée mondiale de la Paix 🕊️ / Nouvel An 🎉",
        (4, 1): "Journée mondiale du braille 🧑‍🦯📖 ",
        (6, 1): "Épiphanie 👑🍰 ",

        # --- FÉVRIER ---
        (4, 2): "Journée mondiale contre le cancer 🎗️",
        (14, 2): "Saint-Valentin ❤️💌",
        (20, 2): "Journée mondiale de la justice sociale ⚖️🤝",
        (21, 2): "Journée internationale de la langue maternelle 🗣️📚",

        # --- MARS ---
        (8, 3): "Journée internationale des droits des femmes 👩‍⚖️♀️",
        (20, 3): "Journée internationale de la Francophonie 🇫🇷🌍",
        (21, 3): "Journée internationale pour l'élimination de la discrimination raciale ✊🏽🤝",
        (22, 3): "Journée mondiale de l'eau 💧🌊",
        (27, 3): "Journée mondiale du théâtre 🎭",

        # --- AVRIL ---
        (7, 4): "Journée mondiale de la santé 🏥💉",
        (22, 4): "Jour de la Terre 🌍🌱",
        (23, 4): "Journée mondiale du livre et du droit d'auteur 📚✍️",
        (25, 4): "Journée mondiale de lutte contre le paludisme 🦟💊",
        (26, 4): "Journée mondiale de la propriété intellectuelle 💡📄",

        # --- MAI ---
        (1, 5): "Fête du Travail 🛠️👷",
        (3, 5): "Journée mondiale de la liberté de la presse 📰✒️",
        (8, 5): "Journée mondiale de la Croix-Rouge 🩸❤️",
        (15, 5): "Journée internationale des familles 👨‍👩‍👧‍👦",
        (17, 5): "Journée mondiale de lutte contre l'homophobie 🌈✊",
        (22, 5): "Journée mondiale de la biodiversité 🐾🌳",
        (31, 5): "Journée mondiale sans tabac 🚭",

        # --- JUIN ---
        (1, 6): "Journée mondiale de l'enfance 🧒👦",
        (5, 6): "Journée mondiale de l'environnement 🌿🌎",
        (8, 6): "Journée mondiale des océans 🌊🐠",
        (14, 6): "Journée mondiale du donneur de sang 🩸💉",
        (20, 6): "Journée mondiale des réfugiés 🏠✈️",
        (21, 6): "Fête de la musique 🎶🎸",
        (26, 6): "Journée internationale contre l'abus et le trafic de drogues 🚫💊",

        # --- JUILLET ---
        (11, 7): "Journée mondiale de la population 👥🌏",
        (14, 7): "Fête nationale française 🇫🇷🎆",
        (18, 7): "Journée Nelson Mandela ✊🏿🌍",
        (30, 7): "Journée internationale de l'amitié 🤝💛",

        # --- AOÛT ---
        (9, 8): "Journée internationale des peuples autochtones 🪶🌿",
        (12, 8): "Journée internationale de la jeunesse 🧑👩",
        (19, 8): "Journée mondiale de l'aide humanitaire 🏥🤲",
        (23, 8): "Journée internationale du souvenir de la traite négrière et de son abolition 🕯️✊🏾",
        (29, 8): "Journée internationale contre les essais nucléaires ☢️🚫",

        # --- SEPTEMBRE ---
        (8, 9): "Journée internationale de l'alphabétisation ✏️📖",
        (15, 9): "Journée internationale de la démocratie 🗳️🏛️",
        (16, 9): "Journée internationale de la protection de la couche d'ozone 🌎🛡️",
        (21, 9): "Journée internationale de la paix 🕊️✌️",
        (27, 9): "Journée mondiale du tourisme 🌍🧳",
        (29, 9): "Journée mondiale du cœur ❤️🫀",

        # --- OCTOBRE ---
        (1, 10): "Journée internationale des personnes âgées 👵👴",
        (4, 10): "Journée mondiale des animaux 🐶🐱",
        (5, 10): "Journée mondiale des enseignants 👩‍🏫👨‍🏫",
        (10, 10): "Journée mondiale de la santé mentale 🧠💚",
        (16, 10): "Journée mondiale de l’alimentation 🍎🥖",
        (17, 10): "Journée internationale pour l’élimination de la pauvreté 💰🚫",
        (24, 10): "Journée des Nations Unies 🇺🇳🌐",
        (31, 10): "Halloween 🎃👻",

        # --- NOVEMBRE ---
        (1, 11): "Toussaint ⛪🕯️",
        (14, 11): "Journée mondiale du diabète 💉🩸",
        (16, 11): "Journée internationale de la tolérance 🤝🌈",
        (20, 11): "Journée internationale des droits de l'enfant 🧒👧",
        (21, 11): "Journée mondiale de la télévision 📺🌍",
        (25, 11): "Journée internationale pour l’élimination de la violence à l’égard des femmes 🚫♀️",

        # --- DÉCEMBRE ---
        (1, 12): "Journée mondiale de lutte contre le sida ❤️🩸",
        (3, 12): "Journée internationale des personnes handicapées ♿🧑‍🦽",
        (10, 12): "Journée des droits de l'homme 🏛️✊",
        (25, 12): "Noël 🎄🎁",
        (31, 12): "Saint-Sylvestre 🎆🥂"
    }
    return journees.get((day, month), None)

def get_historical_event(day, month):
    """Événements historiques marquants"""
    events = {
        # --- JANVIER ---
        (1, 1): "1999 : Passage à l'euro dans 11 pays européens 💶🌍",
        (7, 1): "1610 : Galileo découvre les lunes de Jupiter 🔭🌌",
        (24, 1): "1848 : Découverte de l'or en Californie 🏞️⛏️",

        # --- FÉVRIER ---
        (14, 2): "1876 : Alexander Graham Bell dépose un brevet pour le téléphone ☎️📜",
        (21, 2): "1965 : Malcolm X est assassiné",
        (27, 2): "1933 : Première diffusion d'un film au cinéma parlant aux États-Unis 🎥🎬",

        # --- MARS ---
        (8, 3): "1910 : Premier vol d'une femme pilote, Raymonde de Laroche ✈️👩‍✈️",
        (15, 3): "44 av. J.-C. : Assassinat de Jules César 🏛️⚔️",
        (20, 3): "2003 : Début de la guerre en Irak 🪖",
        (22, 3): "1963 : Martin Luther King prononce 'I Have a Dream' à Birmingham",

        # --- AVRIL ---
        (1, 4): "1976 : Création d'Apple Computer 🍏💻",
        (12, 4): "1961 : Youri Gagarine, premier homme dans l'espace 🚀🌕",
        (15, 4): "1912 : Naufrage du Titanic 🛳️❄️",
        (25, 4): "1953 : Découverte de la structure de l'ADN 🧬",

        # --- MAI ---
        (1, 5): "1886 : Début de la grève de Haymarket à Chicago ✊🏙️",
        (8, 5): "1945 : Fin de la Seconde Guerre mondiale en Europe 🕊️🇪🇺",
        (17, 5): "1954 : Arrêt Brown v. Board of Education aux États-Unis 🗽",
        (29, 5): "1953 : Edmund Hillary et Tenzing Norgay atteignent le sommet de l'Everest 🏔️",

        # --- JUIN ---
        (6, 6): "1944 : Débarquement de Normandie 🪖🌊",
        (16, 6): "1963 : Valentina Terechkova devient la première femme dans l'espace 👩‍🚀🚀",
        (20, 6): "1789 : Serment du Jeu de Paume 📖",
        (26, 6): "1945 : Charte des Nations Unies signée 📑",

        # --- JUILLET ---
        (14, 7): "1789 : Prise de la Bastille 🏰🔥",
        (20, 7): "1969 : Neil Armstrong marche sur la Lune 🌕👨‍🚀",
        (25, 7): "1978 : Naissance de Louise Brown, premier bébé-éprouvette 🍼",

        # --- AOÛT ---
        (6, 8): "1945 : Bombardement atomique d'Hiroshima ☢️💥",
        (9, 8): "1945 : Bombardement atomique de Nagasaki ☢️💥",
        (15, 8): "1947 : Indépendance de l'Inde ",
        (30, 8): "1963 : Martin Luther King prononce 'I Have a Dream' 💭",

        # --- SEPTEMBRE ---
        (11, 9): "2001 : Attentats du World Trade Center 🗽💔",
        (8, 9): "1966 : Première émission de Star Trek",
        (21, 9): "1937 : Début du vol autour du monde de Wiley Post",

        # --- OCTOBRE ---
        (1, 10): "1949 : Proclamation de la République populaire de Chine 🇨🇳🏛️",
        (3, 10): "1990 : Réunification allemande 🇩🇪🤝",
        (12, 10): "1492 : Christophe Colomb découvre l'Amérique ⛵🌎",
        (24, 10): "1929 : Krach boursier de Wall Street 📉💲",

        # --- NOVEMBRE ---
        (9, 11): "1989 : Chute du mur de Berlin 🧱⚡",
        (11, 11): "1918 : Armistice de la Première Guerre mondiale 🕊️",
        (22, 11): "1963 : Assassinat de John F. Kennedy 🕊️",
        (20, 11): "1945 : Fondation de l'UNESCO 🏛️",

        # --- DÉCEMBRE ---
        (7, 12): "1941 : Attaque de Pearl Harbor ⚓💥",
        (10, 12): "1948 : Adoption de la Déclaration universelle des droits de l'homme 📜✊",
        (25, 12): "800 : Couronnement de Charlemagne 👑"

    }
    return events.get((day, month), None)


def get_weather_forecast():
    """Récupère météo via Open-Meteo (aujourd'hui et demain pour comparaison)"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': LATITUDE,
        'longitude': LONGITUDE,
        'hourly': 'temperature_2m,precipitation_probability,weathercode,windspeed_10m,apparent_temperature',
        'daily': 'sunrise,sunset,uv_index_max,temperature_2m_max,temperature_2m_min',
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
    """Extrait prévisions pour 8h, 12h, 16h, 20h de demain + données aujourd'hui"""
    hourly = data.get('hourly', {})
    daily = data.get('daily', {})
    
    times = hourly.get('time', [])
    temps = hourly.get('temperature_2m', [])
    apparent_temps = hourly.get('apparent_temperature', [])
    precip = hourly.get('precipitation_probability', [])
    weather_codes = hourly.get('weathercode', [])
    wind_speeds = hourly.get('windspeed_10m', [])
    
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    today_date = today.strftime('%Y-%m-%d')
    tomorrow_date = tomorrow.strftime('%Y-%m-%d')
    
    forecasts = {}
    
    # Données de demain
    for i, time_str in enumerate(times):
        if tomorrow_date in time_str:
            hour = int(time_str.split('T')[1].split(':')[0])
            if hour in [8, 12, 16, 20]:
                forecasts[hour] = {
                    'temp': temps[i],
                    'feels_like': apparent_temps[i] if i < len(apparent_temps) else temps[i],
                    'precip': precip[i] if i < len(precip) else 0,
                    'weather_code': weather_codes[i],
                    'wind': wind_speeds[i]
                }
    
    # Données d'aujourd'hui pour comparaison
    today_temps = []
    today_precips = []
    today_winds = []
    for i, time_str in enumerate(times):
        if today_date in time_str:
            hour = int(time_str.split('T')[1].split(':')[0])
            if hour in [8, 12, 16, 20]:
                today_temps.append(temps[i])
                today_precips.append(precip[i] if i < len(precip) else 0)
                today_winds.append(wind_speeds[i])
    
    if today_temps:
        forecasts['today_avg_temp'] = sum(today_temps) / len(today_temps)
        forecasts['today_max_precip'] = max(today_precips)
        forecasts['today_avg_wind'] = sum(today_winds) / len(today_winds)
    
    # Températures min/max journalières
    if daily and 'temperature_2m_max' in daily:
        forecasts['today_max_temp'] = daily['temperature_2m_max'][0] if len(daily['temperature_2m_max']) > 0 else None
        forecasts['today_min_temp'] = daily['temperature_2m_min'][0] if len(daily['temperature_2m_min']) > 0 else None
        forecasts['tomorrow_max_temp'] = daily['temperature_2m_max'][1] if len(daily['temperature_2m_max']) > 1 else None
        forecasts['tomorrow_min_temp'] = daily['temperature_2m_min'][1] if len(daily['temperature_2m_min']) > 1 else None
    
    # Données journalières
    if daily and 'sunrise' in daily:
        forecasts['sunrise'] = daily['sunrise'][1] if len(daily['sunrise']) > 1 else None
        forecasts['sunset'] = daily['sunset'][1] if len(daily['sunset']) > 1 else None
        forecasts['uv_max'] = daily['uv_index_max'][1] if len(daily.get('uv_index_max', [])) > 1 else None
    
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

def get_wind_description(speed):
    """Description du vent selon la vitesse"""
    if speed < 10:
        return "Léger"
    elif speed < 20:
        return "Modéré"
    elif speed < 30:
        return "Assez fort"
    elif speed < 40:
        return "Fort"
    else:
        return "Très fort"

def format_weather_bulletin(tomorrow_info, forecasts):
    """Formate le bulletin complet avec style amélioré"""
    if not forecasts:
        return None
    
    day = tomorrow_info['day_num']
    month = tomorrow_info['month']
    date_obj = tomorrow_info['date_obj']
    is_weekend = tomorrow_info['is_weekend']
    
    planned = get_planned_events(date_obj)
    journee = get_journee_mondiale(day, month)
    event = get_historical_event(day, month)
    
    # En-tête avec emoji de jour
    day_emoji = "🎉" if is_weekend else "📅"
    description = f"{day_emoji} **{tomorrow_info['formatted'].upper()}**\n\n"
    
    # Section événements avec encadré
    has_events = False
    if planned:
        has_events = True
        description += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        description += "           🔔 ÉVÉNEMENTS IMPORTANTS    ║\n"
        description += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for p in planned:
            emoji_map = {
                'greve': '🚨',
                'ferie': '🎉',
                'transport': '🚌',
                'autre': 'ℹ️'
            }
            emoji = emoji_map.get(p.get('type', 'autre'), 'ℹ️')
            desc_text = p.get('description', '')[:150]
            description += f"{emoji} **{p['title']}**\n_{desc_text}_\n\n"
    
    # Culture
    culture_section = ""
    if journee:
        culture_section += f"🌍 **{journee}**\n\n"
    if event:
        # Format : "1990 : Description" → "📜 Ce jour en 1990 : Description"
        parts = event.split(':', 1)
        if len(parts) == 2:
            year = parts[0].strip()
            desc = parts[1].strip()
            culture_section += f"📜 **Ce jour en {year}**\n_{desc}_\n\n"
    
    if culture_section:
        if has_events:
            description += "─────────────────────────────\n\n"
        description += culture_section + "\n"
    
    # Séparateur météo stylisé
    description += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    description += "               🌤️ MÉTÉO AU HAVRE
    description += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    # Infos soleil et UV
    if 'sunrise' in forecasts and forecasts['sunrise']:
        sunrise_time = forecasts['sunrise'].split('T')[1][:5]
        sunset_time = forecasts['sunset'].split('T')[1][:5] if 'sunset' in forecasts else "N/A"
        description += f"🌅 Lever : **{sunrise_time}** • 🌇 Coucher : **{sunset_time}**\n"
    
    if 'uv_max' in forecasts and forecasts['uv_max']:
        uv = forecasts['uv_max']
        if uv <= 2:
            uv_text = "Faible"
        elif uv <= 5:
            uv_text = "Modéré"
        elif uv <= 7:
            uv_text = "Élevé"
        else:
            uv_text = "Très élevé"
        description += f"☀️ Indice UV : **{uv:.0f}/10** ({uv_text})\n"
    
    description += "\n"
    
    # Prévisions horaires avec design compact
    hours_config = [
        (8, "🌅", "Matin"),
        (12, "☀️", "Midi"),
        (16, "🌆", "Après-midi"),
        (20, "🌙", "Soirée")
    ]
    
    # ALERTE MÉTÉO si conditions extrêmes
    max_precip = max(f['precip'] for h, f in forecasts.items() if isinstance(h, int))
    avg_wind = sum(f['wind'] for h, f in forecasts.items() if isinstance(h, int)) / 4
    has_alert = False
    
    alert_messages = []
    if max_precip > 85:
        alert_messages.append("🌧️ **Fortes pluies**")
        has_alert = True
    if avg_wind > 40:
        alert_messages.append("💨 **Vents violents**")
        has_alert = True
    
    # Vérifier températures extrêmes
    tomorrow_max = forecasts.get('tomorrow_max_temp')
    tomorrow_min = forecasts.get('tomorrow_min_temp')
    if tomorrow_max and tomorrow_max > 35:
        alert_messages.append("🔥 **Forte chaleur**")
        has_alert = True
    elif tomorrow_min and tomorrow_min < 0:
        alert_messages.append("❄️ **Gel attendu**")
        has_alert = True
    
    if has_alert:
        description += "⚠️ **ALERTE MÉTÉO** ⚠️\n"
        description += " • ".join(alert_messages) + "\n\n"
    
    for hour, emoji, label in hours_config:
        if hour in forecasts:
            f = forecasts[hour]
            
            # Température ressentie
            feels_like = f.get('feels_like', f['temp'])
            feels_diff = feels_like - f['temp']
            feels_text = ""
            if abs(feels_diff) >= 2:
                if feels_diff > 0:
                    feels_text = f" (ressenti {feels_like:.0f}°C)"
                else:
                    feels_text = f" (ressenti {feels_like:.0f}°C)"
            
            # Ligne condensée
            description += f"{emoji} **{label} ({hour}h)** • {get_weather_emoji(f['weather_code'])} {get_weather_description(f['weather_code'])}\n"
            description += f"   🌡️ **{f['temp']:.1f}°C**{feels_text} • 💧 {f['precip']}% • 💨 {f['wind']:.0f} km/h ({get_wind_description(f['wind'])})\n\n"
    
    # Synthèse et conseil
    avg_temp = sum(f['temp'] for h, f in forecasts.items() if isinstance(h, int)) / 4
    max_precip = max(f['precip'] for h, f in forecasts.items() if isinstance(h, int))
    avg_wind = sum(f['wind'] for h, f in forecasts.items() if isinstance(h, int)) / 4
    
    description += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    description += "**📊 RÉSUMÉ DE LA JOURNÉE**\n"
    description += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    description += f"• Température moyenne : **{avg_temp:.1f}°C**\n"
    description += f"• Probabilité de pluie max : **{max_precip:.0f}%**\n"
    description += f"• Vent moyen : **{avg_wind:.0f} km/h**\n"
    
    # COMPARAISON AVEC HIER (Option B)
    if 'today_avg_temp' in forecasts:
        temp_diff = avg_temp - forecasts['today_avg_temp']
        precip_diff = max_precip - forecasts['today_max_precip']
        wind_diff = avg_wind - forecasts['today_avg_wind']
        
        description += "\n**📈 PAR RAPPORT À AUJOURD'HUI**\n"
        
        # Température
        if abs(temp_diff) >= 1:
            if temp_diff > 0:
                description += f"• 🌡️ **+{temp_diff:.1f}°C** plus chaud\n"
            else:
                description += f"• 🌡️ **{temp_diff:.1f}°C** plus frais\n"
        else:
            description += "• 🌡️ Températures similaires\n"
        
        # Précipitations
        if abs(precip_diff) >= 15:
            if precip_diff > 0:
                description += f"• 💧 **+{precip_diff:.0f}%** de risque de pluie\n"
            else:
                description += f"• ☀️ **{abs(precip_diff):.0f}%** moins de risque de pluie\n"
        
        # Vent
        if abs(wind_diff) >= 5:
            if wind_diff > 0:
                description += f"• 💨 Vent plus fort (**+{wind_diff:.0f} km/h**)\n"
            else:
                description += f"• 💨 Vent plus calme (**{wind_diff:.0f} km/h**)\n"
    
    description += "\n"
    
    # Conseils personnalisés
    conseils = []
    if max_precip > 70:
        conseils.append("☂️ **Parapluie obligatoire** - Fortes pluies prévues")
    elif max_precip > 40:
        conseils.append("☂️ Prenez un parapluie par précaution")
    
    if avg_temp < 5:
        conseils.append("🧥 **Habillez-vous chaudement** - Températures fraîches")
    elif avg_temp < 12:
        conseils.append("🧥 Prévoyez une veste")
    elif avg_temp > 25:
        conseils.append("🕶️ Pensez à vous hydrater")
    
    if avg_wind > 30:
        conseils.append("💨 **Vent fort** - Attention aux objets légers")
    elif avg_wind > 20:
        conseils.append("💨 Vent soutenu attendu")
    
    if 'uv_max' in forecasts and forecasts['uv_max'] and forecasts['uv_max'] > 6:
        conseils.append("🧴 Protection solaire recommandée")
    
    if not conseils:
        if is_weekend:
            conseils.append("🎉 Bon week-end au Havre !")
        else:
            conseils.append("👌 Conditions agréables prévues")
    
    description += "**💡 CONSEILS**\n"
    for conseil in conseils:
        description += f"• {conseil}\n"
    
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
    
    # Couleur selon météo dominante
    avg_code = sum(f.get('weather_code', 0) for h, f in forecasts.items() if isinstance(h, int)) / 4
    if avg_code < 3:
        color = 0xFFD700  # Doré (beau temps)
    elif avg_code < 50:
        color = 0x87CEEB  # Bleu ciel (nuageux)
    elif avg_code < 70:
        color = 0x4682B4  # Bleu acier (pluie légère)
    else:
        color = 0x4169E1  # Bleu royal (pluie/orage)
    
    embed = {
        "title": "📰 Bulletin Quotidien du Havre",
        "description": bulletin,
        "color": color,
        "footer": {
            "text": "🤖 Bulletin automatique • Données Open-Meteo • Mis à jour quotidiennement à 20h",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/1163/1163661.png"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    payload = {
        "username": "📰 Bulletin Le Havre",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/1163/1163661.png",
        "content": f"<@&{ROLE_ID}> **Votre bulletin quotidien est arrivé !** 🎯",
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
