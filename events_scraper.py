#!/usr/bin/env python3
"""
Scraper événements - Sources fiables
- LiA Le Havre pour grèves transport
- Actualités pour mouvements sociaux
- Jours fériés officiels
"""
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import re

def scrape_lia_disruptions(debug=True):
    """Scrape les perturbations LiA pertinentes (tramway ou grève) avec logs détaillés"""
    events = []

    try:
        import requests
        from bs4 import BeautifulSoup
        import re
        from datetime import datetime, timedelta

        url = "https://www.transports-lia.fr/fr/infos-trafic/17/Disruption"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        if debug:
            print("🚏 [LiA] Téléchargement de la page des perturbations...")

        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"⚠️ [LiA] Erreur HTTP {resp.status_code}")
            return events

        soup = BeautifulSoup(resp.text, "html.parser")

        # On récupère les articles ou blocs de perturbations
        disruptions = soup.find_all("article") or soup.find_all("div", class_="disruption")
        if debug:
            print(f"📋 [LiA] {len(disruptions)} perturbation(s) trouvée(s) sur la page")

        months_map = {
            'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12
        }

        kept = 0
        for i, item in enumerate(disruptions, 1):
            title = item.get_text(strip=True).lower()
            text = item.get_text(" ", strip=True).lower()

            # Vérifie si c’est pertinent
            if not re.search(r'\b(tram|tramway|gr[eè]ve)\b', title):
                if debug:
                    print(f"❌ Ignoré #{i} (non pertinent) → {title[:60]}...")
                continue

            # Extraction d’un titre lisible
            display_title = item.find("h3").get_text(strip=True) if item.find("h3") else title.title()

            # Recherche de dates dans le texte
            date_patterns = re.findall(
                r'(?:du |le |à partir du )?(\d{1,2})\s+'
                r'(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)',
                text
            )

            # Brève description (30 premiers mots)
            description = " ".join(text.split()[:30]) + "..."
            event_dates = []

            if date_patterns:
                for day, month in date_patterns[:3]:
                    try:
                        month_num = months_map.get(month)
                        year = datetime.now().year
                        if month_num and month_num < datetime.now().month:
                            year += 1
                        d = datetime(year, month_num, int(day))
                        event_dates.append(d)
                    except Exception as e:
                        if debug:
                            print(f"⚠️ Erreur parsing date LiA : {e}")

            # Si aucune date trouvée, on suppose aujourd’hui / demain
            if not event_dates:
                event_dates = [datetime.now(), datetime.now() + timedelta(days=1)]

            for d in event_dates:
                if datetime.now() - timedelta(days=1) <= d <= datetime.now() + timedelta(days=14):
                    event = {
                        "date": d.strftime("%Y-%m-%d"),
                        "type": "greve" if "grève" in text or "greve" in text else "transport",
                        "title": display_title,
                        "description": description,
                        "source": "LiA Transports"
                    }
                    events.append(event)
                    kept += 1
                    if debug:
                        print(f"✅ Gardé #{i}: {display_title} → {d.strftime('%d %b %Y')} ({event['type']})")
                else:
                    if debug:
                        print(f"⏩ Ignoré #{i} (date trop lointaine) → {display_title}")

        if debug:
            print(f"✅ [LiA] {kept} perturbation(s) pertinente(s) gardée(s) sur {len(disruptions)}")

    except Exception as e:
        print(f"⚠️ [LiA] Erreur lors du scraping : {e}")

    return events


def scrape_greves(debug=True):
    """
    Scrape les infos de grèves (France + Le Havre) depuis plusieurs sources médias et open data.
    Ne garde que les grèves futures, pertinentes et sourcées.
    """
    import requests
    from bs4 import BeautifulSoup
    import re
    from datetime import datetime, timedelta

    events = []
    today = datetime.now().date()

    sources = [
        ("https://www.service-public.fr/particuliers/actualites", "Service Public (officiel)"),
        ("https://www.francetvinfo.fr/economie/transports/sncf/", "France Info SNCF"),
        ("https://www.francetvinfo.fr/societe/greve/", "France Info Grèves"),
        ("https://actu.fr/normandie/le-havre/", "Actu.fr Le Havre"),
    ]

    months_map = {
        'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
        'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
        'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12
    }

    if debug:
        print("📰 [Grèves] Scraping des sources d'actualités...")

    for url, label in sources:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if resp.status_code != 200:
                if debug:
                    print(f"⚠️ [{label}] Erreur HTTP {resp.status_code}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.find_all("a", href=True)
            for a in links:
                text = a.get_text(" ", strip=True)
                if not text:
                    continue
                lower = text.lower()

                # 🎯 Filtrage initial
                if not re.search(r"\b(gr[eè]ve|mouvement social|mobilisation|perturbation|sncf|lia|transports?)\b", lower):
                    continue

                # ❌ Ignore les bilans ("bilan", "retard", "incendie", "manifesté", etc.)
                if re.search(r"\b(bilan|retard|manifesté|manifestants?|incendie|retards?|perturbé|passagers|heures de retard)\b", lower):
                    continue

                # ⚙️ Filtrage géographique négatif
                if re.search(r"\b(toulouse|bordeaux|lyon|marseille|nice|lille|strasbourg|nantes|montpellier|rennes)\b", lower):
                    if not re.search(r"\b(le\s*havre|normandie|national|toute la france|sncf|ratp)\b", lower):
                        continue

                href = a["href"]
                if not href.startswith("http"):
                    href = url.rstrip("/") + "/" + href.lstrip("/")

                # 🔍 On tente d'extraire plus d'infos dans l'article
                sub_desc = ""
                try:
                    sub_resp = requests.get(href, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
                    sub_soup = BeautifulSoup(sub_resp.text, "html.parser")
                    paragraphs = sub_soup.find_all("p")
                    if paragraphs:
                        sub_desc = " ".join(p.get_text(" ", strip=True) for p in paragraphs[:3])
                except:
                    pass

                # 🧠 Score de pertinence
                relevance = 0
                if re.search(r"\b(le\s*havre|normandie|lia|universit)\b", lower + sub_desc.lower()):
                    relevance += 2
                if re.search(r"\bnational|sncf|ratp|éducation|enseignants?\b", lower + sub_desc.lower()):
                    relevance += 1
                if relevance == 0:
                    continue

                # 🔎 Extraction de dates (futures uniquement)
                date_matches = re.findall(
                    r"(?:le|du|à partir du)?\s*(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|"
                    r"juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre)\b",
                    (lower + sub_desc.lower())
                )

                future_dates = []
                for day, month in date_matches[:3]:
                    try:
                        m = months_map.get(month.replace("û", "u"))
                        year = today.year
                        if m and m < today.month:
                            year += 1
                        d = datetime(year, m, int(day)).date()
                        # 🔥 On garde uniquement si la date est dans le futur (dans les 60 prochains jours)
                        if today <= d <= today + timedelta(days=60):
                            future_dates.append(d)
                    except Exception as e:
                        if debug:
                            print(f"⚠️ Erreur parsing date dans {label}: {e}")

                # 🧹 Si pas de date future, on ignore
                if not future_dates:
                    continue

                # ✅ Création d'événements
                for d in future_dates:
                    event = {
                        "date": d.strftime("%Y-%m-%d"),
                        "type": "greve",
                        "title": text.strip().capitalize(),
                        "description": (sub_desc[:300] + "...") if sub_desc else "Annonce de grève prochaine.",
                        "source": label,
                        "importance": relevance,
                        "link": href
                    }
                    events.append(event)
                    if debug:
                        print(f"✅ [Grève] {label} → {event['title']} ({event['date']})")

        except Exception as e:
            if debug:
                print(f"⚠️ Erreur scraping {label}: {e}")

    # 🔧 Nettoyage final : supprimer doublons + trier par date
    seen = set()
    filtered = []
    for ev in events:
        key = (ev['date'], ev['title'])
        if key not in seen:
            seen.add(key)
            filtered.append(ev)

    filtered = [e for e in filtered if datetime.strptime(e['date'], "%Y-%m-%d").year == today.year]
    filtered.sort(key=lambda x: x['date'])

    if debug:
        print(f"✅ [Grèves] {len(filtered)} grève(s) future(s) pertinente(s) conservée(s).")

    return filtered


def get_jours_feries():
    """Jours fériés français officiels"""
    events = []
    current_year = datetime.now().year
    
    jours_feries_fixes = [
        (1, 1, "Jour de l'an"),
        (5, 1, "Fête du Travail"),
        (5, 8, "Victoire 1945"),
        (7, 14, "Fête Nationale"),
        (8, 15, "Assomption"),
        (11, 1, "Toussaint"),
        (11, 11, "Armistice 1918"),
        (12, 25, "Noël")
    ]
    
    for year in [current_year, current_year + 1]:
        for month, day, nom in jours_feries_fixes:
            date = datetime(year, month, day)
            if datetime.now() <= date <= datetime.now() + timedelta(days=30):
                events.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'type': 'ferie',
                    'title': nom,
                    'description': 'Jour férié - Services publics fermés',
                    'source': 'Calendrier officiel'
                })
    
    # Jours mobiles
    paques_dates = {
        2024: datetime(2024, 3, 31),
        2025: datetime(2025, 4, 20),
        2026: datetime(2026, 4, 5)
    }
    
    for year, paques in paques_dates.items():
        lundi_paques = paques + timedelta(days=1)
        ascension = paques + timedelta(days=39)
        pentecote = paques + timedelta(days=50)
        
        for date, nom in [(lundi_paques, "Lundi de Pâques"), 
                          (ascension, "Ascension"), 
                          (pentecote, "Lundi de Pentecôte")]:
            if datetime.now() <= date <= datetime.now() + timedelta(days=30):
                events.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'type': 'ferie',
                    'title': nom,
                    'description': 'Jour férié',
                    'source': 'Calendrier officiel'
                })
    
    return events

def merge_and_deduplicate(events):
    """Fusionne et déduplique"""
    seen = set()
    unique = []
    
    for event in events:
        key = (event['date'], event['title'])
        if key not in seen:
            seen.add(key)
            unique.append(event)
    
    unique.sort(key=lambda x: x['date'])
    return unique

def save_events(events):
    """Sauvegarde dans planned_events.json"""
    output = {
        'last_update': datetime.now().isoformat(),
        'events': events
    }
    
    with open('planned_events.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Sauvegardé {len(events)} événements")

def main():
    print("="*60)
    print("SCRAPER ÉVÉNEMENTS")
    print(f"Exécution: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*60)
    
    all_events = []
    
    print("\n📅 Jours fériés...")
    feries = get_jours_feries()
    all_events.extend(feries)
    print(f"  ✓ {len(feries)} jours fériés")
    
    print("\n🚌 Perturbations LiA...")
    lia = scrape_lia_disruptions()
    all_events.extend(lia)
    print(f"  ✓ {len(lia)} perturbations LiA")
    
    print("\n📰 Mouvements sociaux...")
    greves = scrape_greves()
    all_events.extend(greves)
    print(f"  ✓ {len(greves)} mouvements sociaux")
    
    unique = merge_and_deduplicate(all_events)
    save_events(unique)
    
    print(f"\n✅ TOTAL: {len(unique)} événements")
    
    if unique:
        print("\n📋 Prochains événements:")
        for event in unique[:5]:
            print(f"  • {event['date']} - {event['title']}")


if __name__ == "__main__":
    main()
