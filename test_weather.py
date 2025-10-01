#!/usr/bin/env python3
"""Test du bulletin météo"""
import requests
from datetime import datetime, timedelta

WEBHOOK = "https://discord.com/api/webhooks/1423015970523320320/NEeoliSALJV-OORt_cDezxiqeX6fugRUSUqurjLPIwbvawBrbb6wAWHIVHBo7S1YPjSX"
ROLE_ID = "1423013715594444821"

def test_bulletin():
    """Envoie un bulletin de test"""
    
    tomorrow = datetime.now() + timedelta(days=1)
    
    bulletin = f"""
📅 **TEST BULLETIN - {tomorrow.strftime('%A %d %B %Y').upper()}**

🎉 **Test du système de bulletin**

📖 **Le saviez-vous ?**
Ceci est un test du système automatique de bulletin quotidien.

━━━━━━━━━━━━━━━━━━━━━━
🌤️ **PRÉVISIONS MÉTÉO TEST**
━━━━━━━━━━━━━━━━━━━━━━

🌅 **MATIN (8h)**
☀️ Ciel dégagé
🌡️ Température : **15.0°C**
💧 Précipitations : 10%
💨 Vent : 12 km/h

☀️ **MIDI (12h)**
🌤️ Peu nuageux
🌡️ Température : **18.5°C**
💧 Précipitations : 5%
💨 Vent : 15 km/h

🌆 **APRÈS-MIDI (16h)**
☁️ Nuageux
🌡️ Température : **17.0°C**
💧 Précipitations : 20%
💨 Vent : 18 km/h

🌙 **SOIRÉE (20h)**
🌧️ Pluie légère
🌡️ Température : **14.0°C**
💧 Précipitations : 60%
💨 Vent : 20 km/h

💡 **Conseil du jour :** Temps agréable prévu !
"""
    
    embed = {
        "title": "🧪 TEST - Bulletin Quotidien",
        "description": bulletin.strip(),
        "color": 0x3498db,
        "footer": {"text": "TEST - Bulletin automatique"},
        "timestamp": datetime.now().isoformat()
    }
    
    payload = {
        "username": "📰 Bulletin Quotidien (TEST)",
        "content": f"<@&{ROLE_ID}>",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(WEBHOOK, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Test envoyé (status: {response.status_code})")
        print("\nVérifiez Discord - vous devriez voir:")
        print("  - Mention du rôle Bulletin")
        print("  - Prévisions météo test sur 4 créneaux")
        print("  - Saint du jour et événement historique")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test du bulletin météo")
    print("="*50)
    test_bulletin()
