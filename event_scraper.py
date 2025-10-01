#!/usr/bin/env python3
"""
Scraper automatique pour récupérer les grèves et événements en France
Sources : flux RSS, sites officiels
"""
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import re

def scrape_greves_transports():
    """Scrape les perturbations transport depuis diverses sources"""
    events = []
    
    # Source 1: SNCF (via leur API publique si disponible)
    try:
        # API SNCF open data pour les perturbations
        url = "https://data.sncf.com/api/records/1.0/search/"
        params = {
            'dataset': 'evenements-sur-le-reseau-ferre-sncf',
            'rows': 20,
            'sort': '-date_de_debut'
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for record in data.get('records', []):
                fields = record.get('fields', {})
                date_str = fields.get('date_de_debut', '')
                if date_str:
                    # Parser et vérifier si c'est dans les 7 prochains jours
                    try:
                        event_date = datetime.fromisoformat(date_str.split('T')[0])
                        if datetime.now() <= event_date <= datetime.now() + timedelta(days=7):
                            events.append({
                                'date': event_date.strftime('%Y-%m-%d'),
                                'type': 'transport',
                                'title': fields.get('titre', 'Perturbation SNCF'),
                                'description': fields.get('message', '')[:200],
                                'source': 'SNCF'
                            })
                    except:
                        pass
    except Exception as e:
        print(f"Erreur SNCF: {e}")
    
    return events

def scrape_greves_fonction_publique():
    """Tente de récupérer les appels à la grève fonction publique"""
    events = []
    
    # Recherche via Google News API ou flux RSS
    try:
        # Utiliser une recherche de mots-clés sur des flux RSS d'actualités
        rss_sources = [
            'https://www.francetvinfo.fr/titres.rss',
            'https://www.lemonde.fr/rss/une.xml'
        ]
        
        keywords = ['grève', 'mouvement social', 'manifestation', 'préavis']
        
        for rss_url in rss_sources:
            try:
                resp = requests.get(rss_url, timeout=10)
                if resp.status_code == 200:
                    content = resp.text
                    # Recherche simple de patterns
                    for keyword in keywords:
                        if keyword in content.lower():
                            # Extraire des dates potentielles
                            date_patterns = re.findall(r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)', content.lower())
                            for day, month in date_patterns[:3]:  # Limiter à 3
                                try:
                                    months_map = {
                                        'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
                                        'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
                                        'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
                                    }
                                    month_num = months_map.get(month)
                                    if month_num:
                                        year = datetime.now().year
                                        event_date = datetime(year, month_num, int(day))
                                        if datetime.now() <= event_date <= datetime.now() + timedelta(days=14):
                                            events.append({
                                                'date': event_date.strftime('%Y-%m-%d'),
                                                'type': 'greve',
                                                'title': f'Mouvement social annoncé',
                                                'description': f'Mouvement social mentionné dans l\'actualité pour le {day} {month}',
                                                'source': 'Actualités'
                                            })
                                except:
                                    pass
            except:
                pass
    except Exception as e:
        print(f"Erreur flux RSS: {e}")
    
    return events

def get_jours_feries():
    """Retourne les jours fériés français pour l'année en cours et suivante"""
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
    
    # Pâques et jours mobiles (calcul simplifié)
    # Pour 2024: Pâques = 31 mars, pour 2025: 20 avril
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
    """Fusionne et déduplique les événements"""
    seen = set()
    unique_events = []
    
    for event in events:
        key = (event['date'], event['title'])
        if key not in seen:
            seen.add(key)
            unique_events.append(event)
    
    # Trier par date
    unique_events.sort(key=lambda x: x['date'])
    
    return unique_events

def save_events(events):
    """Sauvegarde les événements dans le fichier JSON"""
    output = {
        'last_update': datetime.now().isoformat(),
        'events': events,
        'instructions': 'Fichier mis à jour automatiquement. Ne pas modifier manuellement.'
    }
    
    with open('planned_events.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Sauvegardé {len(events)} événements")

def main():
    print("="*60)
    print("SCRAPER ÉVÉNEMENTS AUTOMATIQUE")
    print(f"Exécution: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*60)
    
    all_events = []
    
    # Récupérer les jours fériés (toujours fiables)
    print("\nRécupération jours fériés...")
    feries = get_jours_feries()
    all_events.extend(feries)
    print(f"  Trouvé: {len(feries)} jours fériés")
    
    # Tenter de récupérer les grèves transport
    print("\nRecherche perturbations transport...")
    try:
        transport = scrape_greves_transports()
        all_events.extend(transport)
        print(f"  Trouvé: {len(transport)} perturbations transport")
    except Exception as e:
        print(f"  Erreur: {e}")
    
    # Tenter de récupérer les mouvements sociaux
    print("\nRecherche mouvements sociaux...")
    try:
        greves = scrape_greves_fonction_publique()
        all_events.extend(greves)
        print(f"  Trouvé: {len(greves)} mouvements sociaux")
    except Exception as e:
        print(f"  Erreur: {e}")
    
    # Nettoyer et sauvegarder
    unique_events = merge_and_deduplicate(all_events)
    save_events(unique_events)
    
    print("\n" + "="*60)
    print(f"RÉSUMÉ: {len(unique_events)} événements à venir")
    print("="*60)
    
    # Afficher les prochains événements
    for event in unique_events[:5]:
        print(f"  {event['date']} - {event['title']}")

if __name__ == "__main__":
    main()
