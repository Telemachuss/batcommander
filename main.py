import json
from bot import bot
import os
import asyncio
import datetime
import test

# Laden der Konfigurationsdatei
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

@bot.event
async def on_ready():
    print(f"{bot.user} ist online")

async def clean_files():
    while True:
        now = datetime.datetime.now()

        # Lösche alle Dateien, die älter als eine Minute sind
        for file in os.listdir("swgohreq"):
            filepath = os.path.join("swgohreq", file)
            if os.path.isfile(filepath):
                mod_time = os.path.getmtime(filepath)
                if (now - datetime.datetime.fromtimestamp(mod_time)) > datetime.timedelta(minutes=1):
                    os.remove(filepath)

        await asyncio.sleep(60)

async def main():
    # Starte die Schleife zur automatischen Bereinigung der Dateien im Hintergrund
    asyncio.create_task(clean_files())

    # Bot-Token aus der Konfigurationsdatei lesen
    bot_token = config['token']

    # Bot starten
    await bot.start(bot_token)

# Starte das Hauptprogramm
asyncio.run(main())
