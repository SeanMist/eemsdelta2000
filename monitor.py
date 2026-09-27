import time
import subprocess
import requests
import shutil
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime, date

# ==============================================================================
# CONFIGURATIE & INSTELLINGEN
# ==============================================================================
DASHBOARD_URL = "https://seanmist.github.io/eemsdelta2000/"
DEVICE_NAME = "woonkamer"

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_OUTPUT_FILE = os.path.join(REPO_DIR, "p2000.json")

# Betrouwbare P2000 RSS-feeds
FEEDS = [
    "https://feed.alarmeringen.nl/groningen.rss",
    "https://feed.alarmeringen.nl/eemsdelta.rss"
]

# Catt automatisch vinden op de pc
CATT_PATH = shutil.which("catt") or shutil.which("catt.exe")
if not CATT_PATH:
    appdata = os.environ.get("LOCALAPPDATA", "")
    possible_paths = [
        os.path.join(appdata, r"Python\pythoncore-3.14-64\Scripts\catt.exe"),
        os.path.join(appdata, r"Programs\Python\Python312\Scripts\catt.exe"),
        r"C:\Python312\Scripts\catt.exe"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            CATT_PATH = path
            break

def start_silent_cast():
    if not CATT_PATH:
        print("❌ FOUT: catt.exe niet gevonden!")
        return
    print(f"📺 Dashboard stilletjes laden op '{DEVICE_NAME}'...")
    try:
        subprocess.run([CATT_PATH, "-d", DEVICE_NAME, "cast_site", DASHBOARD_URL], check=True)
    except Exception as e:
        print(f"⚠️ Cast fout: {e}")

def update_and_push_p2000():
    """Haalt live P2000 op via proxy, filtert op vandaag, en pusht naar GitHub."""
    all_items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    huidige_dag = date.today()

    for feed_url in FEEDS:
        try:
            root = None
            # Probeer eerst direct te laden
            try:
                res = requests.get(feed_url, headers=headers, timeout=5)
                if res.status_code == 200:
                    root = ET.fromstring(res.content)
            except:
                pass

            # Als direct falen optreedt, gebruik de Allorigins proxy met verhoogde time-out
            if root is None:
                proxy_url = f"https://api.allorigins.win/get?url={requests.utils.quote(feed_url)}"
                try:
                    proxy_res = requests.get(proxy_url, timeout=15)
                    if proxy_res.status_code == 200:
                        content = proxy_res.json().get("contents", "")
                        if content:
                            root = ET.fromstring(content)
                except Exception as proxy_err:
                    print(f"⚠️ Proxy verbinding vertraagd voor {feed_url}, even geduld...")

            if root is None:
                continue

            for item in root.findall(".//item"):
                title_elem = item.find("title")
                date_elem = item.find("pubDate")
                
                title = title_elem.text if title_elem is not None else "Geen omschrijving"
                pub_date_str = date_elem.text if date_elem is not None else ""

                try:
                    pub_dt = datetime.strptime(pub_date_str[:25], "%a, %d %b %Y %H:%M:%S")
                    
                    # STRIKTE FILTER: Alleen meldingen van vandaag toelaten
                    if pub_dt.date() != huidige_dag:
                        continue

                    date_str = pub_dt.strftime("%d-%m-%Y")
                    time_str = pub_dt.strftime("%H:%M:%S")
                except:
                    continue

                lower_title = title.lower()
                badge = "MELDING"
                bClass = "bg-info"
                if "prio 1" in lower_title or "a1" in lower_title or "brand" in lower_title or "ongeval" in lower_title or "spoed" in lower_title:
                    badge = "PRIO 1"
                    bClass = "bg-prio1"
                elif "prio 2" in lower_title or "a2" in lower_title or "ambu" in lower_title:
                    badge = "PRIO 2"
                    bClass = "bg-prio2"

                all_items.append({
                    "date": date_str,
                    "time": time_str,
                    "badge": badge,
                    "bClass": bClass,
                    "text": title
                })
        except Exception as e:
            print(f"⚠️ Fout bij ophalen feed {feed_url}: {e}")

    if all_items:
        with open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_items, f, ensure_ascii=False, indent=2)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] P2000 JSON bijgewerkt. Bezig met pushen naar GitHub...")
        
        try:
            subprocess.run(["git", "add", "p2000.json"], cwd=REPO_DIR, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Auto-update live P2000 data via proxy"], cwd=REPO_DIR, capture_output=True)
            push_res = subprocess.run(["git", "push"], cwd=REPO_DIR, capture_output=True, text=True)
            
            if push_res.returncode == 0:
                print("🚀 Succesvol gepusht naar GitHub!")
            else:
                print(f"ℹ️ Git melding: {push_res.stderr.strip()}")
        except Exception as git_err:
            print(f"⚠️ Git synchronisatie fout: {git_err}")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Geen nieuwe meldingen van vandaag gevonden in de feed.")

# ==============================================================================
# HOOFDPROGRAMMA
# ==============================================================================
print("==================================================")
print("🤖 Eemsdelta Ultimate Bridge & Live Monitor (Proxy)")
print(f"🔗 Dashboard: {DASHBOARD_URL}")
print(f"📺 Doelapparaat: {DEVICE_NAME}")
print("==================================================")

start_silent_cast()

print("\n🟢 Monitor draait via proxy en haalt live data binnen.")

while True:
    try:
        update_and_push_p2000()
    except Exception as e:
        print(f"⚠️ Fout in hoofdloop: {e}")
    
    time.sleep(120)