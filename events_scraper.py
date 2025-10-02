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

def scrape_lia_disruptions():
    """Scrape perturbations LiA"""
    events = []
    
    try:
        url = "https://www.transports-lia.fr/fr/infos-trafic/17/Disruption"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Recherche de perturbations dans le contenu
                text_content = soup.get_text().lower()
                
                # Mots-clés de perturbation
                keywords = ['grève', 'greve', 'perturbation', 'interruption', 'travaux']
                
                if any(kw in text_content for kw in keywords):
                    # Recherche de dates
                    months_map = {
                        'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
                        'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
                        'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12
                    }
                    
                    # Pattern: "du X au Y mois" ou "le X mois"
                    date_patterns = re.findall(
                        r'(?:du |le |à partir du )?(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)',
                        text_content
                    )
                    
                    for day, month in date_patterns[:3]:
                        try:
                            month_num = months_map.get(month)
                            if month_num:
                                year = datetime.now().year
                                if month_num < datetime.now().month:
                                    year += 1
                                
                                event_date = datetime(year, month_num, int(day))
                                
                                if datetime.now() <= event_date <= datetime.now() + timedelta(days=14):
                                    events.append({
                                        'date': event_date.strftime('%Y-%m-%d'),
                                        'type': 'greve',
                                        'title': 'Perturbation réseau LiA',
                                        'description': f'Perturbation annoncée sur le réseau LiA - Consultez transports-lia.fr',
                                        'source': 'LiA Transports'
                                    })
                        except:
                            pass
                    
                    # Si aucune date trouvée mais perturbation mentionnée
                    if not date_patterns and any(kw in text_content for kw in keywords):
                        # Supposer que c'est pour aujourd'hui/demain
                        for offset in [0, 1]:
                            event_date = datetime.now() + timedelta(days=offset)
                            events.append({
                                'date': event_date.strftime('%Y-%m-%d'),
                                'type': 'greve',
                                'title': 'Perturbation réseau LiA',
                                'description': 'Perturbation en cours ou à venir - Consultez transports-lia.fr',
                                'source': 'LiA Transports'
                            })
            except ImportError:
                print("⚠️ BeautifulSoup non disponible, analyse basique")
                # Fallback sans BeautifulSoup
                if 'grève' in resp.text.lower() or 'perturbation' in resp.text.lower():
                    event_date = datetime.now() + timedelta(days=1)
                    events.append({
                        'date': event_date.strftime('%Y-%m-%d'),
                        'type': 'greve',
                        'title': 'Perturbation réseau LiA',
                        'description': 'Vérifiez les infos trafic sur transports-lia.fr',
                        'source': 'LiA Transports'
                    })
    
    except Exception as e:
        print(f"⚠️ Erreur LiA: {e}")
    
    return events

def scrape_mouvements_sociaux():
    """Scrape actualités pour mouvements sociaux"""
    events = []
    
    try:
        rss_sources = [
            'https://www.francetvinfo.fr/titres.rss',
            'https://www.lemonde.fr/rss/une.xml'
        ]
        
        keywords = ['grève', 'greve', 'mouvement social', 'manifestation', 'préavis']
        
        months_map = {
            'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12
        }
        
        for rss_url in rss_sources:
            try:
                resp = requests.get(rss_url, timeout=10)
                if resp.status_code == 200:
                    content = resp.text.lower()
                    
                    for keyword in keywords:
                        if keyword in content:
                            # Extraire dates
                            date_patterns = re.findall(
                                r'(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)',
                                content
                            )
                            
                            for day, month in date_patterns[:2]:
                                try:
                                    month_num = months_map.get(month)
                                    if month_num:
                                        year = datetime.now().year
                                        if month_num < datetime.now().month:
                                            year += 1
                                        
                                        event_date = datetime(year, month_num, int(day))
                                        
                                        if datetime.now() <= event_date <= datetime.now() + timedelta(days=14):
                                            events.append({
                                                'date': event_date.strftime('%Y-%m-%d'),
                                                'type': 'greve',
                                                'title': 'Mouvement social annoncé',
                                                'description': 'Mouvement social mentionné dans l\'actualité',
                                                'source': 'Actualités'
                                            })
                                except:
                                    pass
                            break
            except:
                pass
                
    except Exception as e:
        print(f"⚠️ Erreur actualités: {e}")
    
    return events

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
    greves = scrape_mouvements_sociaux()
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
