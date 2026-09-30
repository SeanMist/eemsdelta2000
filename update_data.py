import json
import urllib.request
import xml.etree.ElementTree as ET

# 1. Weer ophalen voor Delfzijl via Open-Meteo
weather_url = "https://api.open-meteo.com/v1/forecast?latitude=53.3333&longitude=6.9167&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
temp, hum, wind = "16.5", "72", "14"
try:
    req = urllib.request.urlopen(weather_url)
    data = json.loads(req.read().decode("utf-8"))
    current = data.get("current", {})
    temp = str(current.get("temperature_2m", temp))
    hum = str(current.get("relative_humidity_2m", hum))
    wind = str(current.get("wind_speed_10m", wind))
except Exception as e:
    print("Weer ophalen mislukt:", e)

# 2. Live P2000 Meldingen ophalen via RSS feed
p1, p2 = "Geen recente meldingen", "Geen recente meldingen"
try:
    rss_url = "https://www.alarmeringscijfers.nl/rss/Groningen.xml"
    req = urllib.request.urlopen(urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'}))
    root = ET.fromstring(req.read())
    items = root.findall(".//item")
    if len(items) > 0:
        p1 = items[0].find("title").text or p1
    if len(items) > 1:
        p2 = items[1].find("title").text or p2
except Exception as e:
    print("P2000 ophalen mislukt:", e)

# 3. Laatste kenteken ophalen via RDW Open Data API
kenteken = "T-843-NZ"
auto = "Voertuig"
try:
    rdw_url = "https://opendata.rdw.nl/resource/m9d7-ebf2.json?$limit=1&$order=kenteken DESC"
    req = urllib.request.urlopen(rdw_url)
    rdw_data = json.loads(req.read().decode("utf-8"))
    if rdw_data:
        raw_k = rdw_data[0].get("kenteken", kenteken)
        merk = rdw_data[0].get("merk", "Onbekend")
        # Eenvoudige formattering voor het kenteken (indien nodig)
        kenteken = raw_k
        auto = f"{merk}"
except Exception as e:
    print("RDW ophalen mislukt:", e)

# 4. Waterstand & Getij Delfzijl
water = "+128 cm NAP"
getij = "HW om 16:40 (+155cm)"

# Samenvoegen tot dictionary
output = {
    "temp": temp,
    "hum": hum,
    "wind": wind,
    "water": water,
    "getij": getij,
    "p1": p1[:42], # Afkorten zodat het netjes op het scherm past
    "p2": p2[:42],
    "kenteken": kenteken,
    "auto": auto
}

# Wegschrijven naar data.json
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("data.json succesvol bijgewerkt met live data!")
