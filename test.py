from bot import bot
import os
import requests
import json
import datetime
import re

# Laden der Konfigurationsdatei
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

@bot.slash_command(name="swgoh", description="Führt eine Abfrage auf swgoh.gg durch")
async def swgoh(ctx, link: str):
    # Überprüfe, ob der Link das erwartete Muster aufweist
    if not re.match(r"https?://swgoh\.gg/(u|p)/\d+/$", link):
        await ctx.respond("Ungültiger Link. Der Link muss zu swgoh.gg führen und entweder '/u/' oder '/p/' gefolgt von einer Zahlenreihe enthalten.")
        return

    # Extrahiere die Player-ID aus dem Link
    player_id = re.search(r"/(u|p)/(\d+)/$", link).group(2)

    # Erstelle die API-URL mit der extrahierten Player-ID
    url = f"http://api.swgoh.gg/player/{player_id}/"

    # Führe die API-Abfrage durch
    response = requests.get(url)

    # Überprüfe den Statuscode der Antwort
    if response.status_code == 200:
        # Konvertiere die Antwort in JSON
        data = response.json()

        # Setze den Filenamen basierend auf dem Namen des Aufrufenden und der aktuellen Uhrzeit
        now = datetime.datetime.now()
        user_filename = f"{ctx.author.name}_{now.strftime('%Y-%m-%d-%H-%M-%S')}.json"
        filename = os.path.join("swgohreq", user_filename)

        # Speichere das Ergebnis in einer JSON-Datei, wenn sie nicht bereits existiert
        if not os.path.isfile(filename):
            with open(filename, "w+") as file:
                json.dump(data, file)
                await ctx.respond(f"Ergebnis wurde erfolgreich in {filename} gespeichert.")
        else:
            with open(filename, "w+") as file:
                json.dump(data, file)
                await ctx.respond(f"Ergebnis wurde erfolgreich in {filename} überschrieben.")


        # Warte, bis die Datei erstellt wurde, bevor du versuchst, sie zu öffnen und auszugeben
        while not os.path.isfile(filename):
            await asyncio.sleep(0.5)

        # Lies Daten aus der Datei und gib sie in Discord aus
        with open(filename, "r") as file:
            data = json.load(file)
            character = data["units"][0]
            base_id = character["data"]["base_id"]
            name = character["data"]["name"]
            await ctx.respond(f"Dein bestes Charakter in SWGoH ist {name} ({base_id}).")
