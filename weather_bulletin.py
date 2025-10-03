#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import urllib.request
from datetime import datetime, timedelta

# Configuration
WEBHOOK_URL = "https://discord.com/api/webhooks/1423592552010879047/NvllOZNsIIHNWj1MzhRVSf-xWHvJKsCtiguyaJcMmQcc5R2WQNcEjjkAY4Do17VXOLlT"
ROLE_ID = "1423592204429164584"
ICAL_URL = "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_Gr1___L2_INFO.ics?version=2022.0.5.0&idICal=63D02C34E55C4FDF72F91012A61BEEEC&param=643d5b312e2e36325d2666683d3126663d3131313030"


def download_calendar():
    req = urllib.request.Request(ICAL_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')


def parse_ical_datetime(dt_string):
    try:
        dt_clean = dt_string.strip().replace('Z', '')
        if 'T' in dt_clean and len(dt_clean) >= 15:
            date_part = dt_clean.split('T')[0]
            year, month, day = int(date_part[:4]), int(date_part[4:6]), int(date_part[6:8])
            return datetime(year, month, day).date()
        elif len(dt_clean) == 8:
            return datetime.strptime(dt_clean, "%Y%m%d").date()
    except Exception as e:
        print(f"⚠️ Erreur parsing datetime {dt_string}: {e}")
    return None


def parse_events(ical_content):
    events = []
    today = datetime.now().date()
    keywords = ['vacances', 'férié', 'holiday', 'congé', 'pont', 'vacation', 'ferie']

    raw_lines = ical_content.split("\n")
    lines, current = [], ""
    for line in raw_lines:
        if line.startswith(" ") or line.startswith("\t"):
            current += line[1:]
        else:
            if current:
                lines.append(current)
            current = line
    if current:
        lines.append(current)

    in_event, current_event = False, {}
    for line in lines:
        line = line.strip()
        if line == "BEGIN:VEVENT":
            in_event, current_event = True, {}
        elif line == "END:VEVENT":
            if in_event and "SUMMARY" in current_event and "DTSTART" in current_event:
                summary = current_event["SUMMARY"].replace("\\n", " ").strip()
                if any(k in summary.lower() for k in keywords):
                    start = parse_ical_datetime(current_event["DTSTART"])
                    end = parse_ical_datetime(current_event.get("DTEND", "")) or start
                    if end and end > start:
                        end -= timedelta(days=1)
                    if start and (start >= today or (end and end >= today)):
                        events.append({"summary": summary, "start": start, "end": end})
            in_event = False
        elif in_event and ":" in line:
            k, v = line.split(":", 1)
            current_event[k.split(";")[0]] = v

    return sorted(events, key=lambda x: x["start"])


def guess_vacation_name(summary, start, end):
    s = summary.lower()
    if "toussaint" in s or (start.month == 10 and end and end.month == 11):
        return "Vacances de la Toussaint 🍂"
    if "noel" in s or "noël" in s or (start.month == 12 or (end and end.month == 1)):
        return "Vacances de Noël 🎅🎄"
    if "hiver" in s or (start.month == 2 or (end and end.month == 3)):
        return "Vacances d'Hiver ❄️"
    if "printemps" in s or (start.month == 4 or (end and end.month == 5)):
        return "Vacances de Printemps 🌸"
    if "ascension" in s:
        return "Pont de l'Ascension 🇫🇷"
    if "ete" in s or "été" in s or start.month >= 7:
        return "Vacances d'Été 🌞"
    if "ferie" in s or "férié" in s or "holiday" in s or "congé" in s:
        return "Jour Férié 🇫🇷"
    return summary.strip()


def merge_consecutive_events(events):
    merged = []
    for evt in events:
        name = guess_vacation_name(evt['summary'], evt['start'], evt['end'])
        if merged and guess_vacation_name(merged[-1]['summary'], merged[-1]['start'], merged[-1]['end']) == name:
            if evt['start'] <= merged[-1]['end'] + timedelta(days=1):
                merged[-1]['end'] = max(merged[-1]['end'], evt['end'])
                continue
        merged.append(evt)
    return merged


def format_countdown(days_until):
    if days_until == 0:
        return "🎉 **C'EST AUJOURD'HUI !** 🎉"
    elif days_until == 1:
        return "⏰ **DEMAIN !** ⏰"
    elif days_until <= 7:
        return f"🔥 **J-{days_until}** 🔥"
    elif days_until <= 30:
        return f"⚡ **J-{days_until}** ⚡"
    else:
        return f"📅 **J-{days_until}** 📅"


def format_date_range(event):
    months = ['', 'janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
    start, end = event['start'], event['end']
    duration = (end - start).days + 1 if end else 1
    pont_text = " (Jour Férié + Pont)" if 2 <= duration <= 3 else ""
    if end and end != start:
        duration_text = f"{duration} jours"
        return f"📆 Du {start.day} {months[start.month]} au {end.day} {months[end.month]} {end.year}\n🕐 Durée : {duration_text}{pont_text}"
    else:
        return f"📆 Le {start.day} {months[start.month]} {start.year}"


def create_progress_bar(days_until, total_days=90):
    if days_until > total_days:
        days_until = total_days
    progress = 1 - (days_until / total_days)
    filled = int(progress * 10)
    empty = 10 - filled
    percentage = int(progress * 100)
    block = "🟩" if percentage > 75 else "🟧" if percentage > 25 else "🟥"
    bar = block * filled + "⬜" * empty
    return f"{bar} {percentage}%\n({days_until} jours restants sur {total_days})"


def create_embed(events):
    today = datetime.now().date()
    if not events:
        return {
            "username": "📚 HyperPlanning Assistant",
            "content": f"<@&{ROLE_ID}>",
            "embeds": [{
                "title": "🔍 Aucune vacance trouvée",
                "description": "Aucune vacances prévues pour l'instant.\n\nTiens bon 💪",
                "color": 0x95A5A6
            }]
        }

    next_event = events[0]
    days_until = (next_event['start'] - today).days
    event_name = guess_vacation_name(next_event['summary'], next_event['start'], next_event['end'])

    description_parts = [
        format_countdown(days_until), "",
        f"🏖️ **{event_name}**", "",
        format_date_range(next_event), "",
        "✨ Garde le rythme, ça arrive vite ! ✨", "",
        "**Progression :**",
        create_progress_bar(days_until)
    ]
    description = "\n".join(description_parts)

    embed = {
        "title": "📅 Prochaines Vacances 📅",
        "description": description,
        "color": 0x3498DB,
        "footer": {"text": "Université Le Havre Normandie"},
        "timestamp": datetime.now().isoformat()
    }

    if len(events) > 1:
        upcoming = []
        for i, evt in enumerate(events[1:4], 1):
            evt_name = guess_vacation_name(evt['summary'], evt['start'], evt['end'])
            months = ['', 'janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
            date_text = f"📆 Du {evt['start'].day} {months[evt['start'].month]} au {evt['end'].day} {months[evt['end'].month]} {evt['end'].year}"
            duration = (evt['end'] - evt['start']).days + 1 if evt['end'] else 1
            duration_text = f"{duration} jours"
            if 2 <= duration <= 3:
                duration_text += " (Jour Férié + Pont)"
            emoji = '📌' if i == 1 else '📍' if i == 2 else '📎'
            upcoming.append(f"{emoji} {evt_name}\n{date_text}\n🕐 Durée : {duration_text}\n")
        embed['fields'] = [{"name": "🗓️ À suivre :", "value": "\n".join(upcoming), "inline": False}]

    return {
        "username": "📚 HyperPlanning Assistant",
        "content": f"<@&{ROLE_ID}>",
        "embeds": [embed]
    }


def send_to_discord(payload):
    req = urllib.request.Request(WEBHOOK_URL,
                                 data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            print(f"✅ Envoyé (Status: {response.status})")
            return True
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False


def main():
    ical_content = download_calendar()
    events = parse_events(ical_content)
    events = merge_consecutive_events(events)
    payload = create_embed(events)
    send_to_discord(payload)


if __name__ == "__main__":
    main()
