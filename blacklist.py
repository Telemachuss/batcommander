import discord
import aiofiles
import re
import json
from bs4 import BeautifulSoup
import requests
from bot import bot
from discord.ext import commands

blacklist = []  # Leere Blacklist zum Speichern der Einträge


@bot.event
async def on_ready():
    print(f"{bot.user} ist online")
    await load_blacklist()  # Blacklist beim Start des Bots laden


import discord


@bot.slash_command(description="Speichert die Rollen-ID für die Blacklist-Permissions.")
@commands.has_permissions(administrator=True)
async def set_required_role(ctx, role: discord.Role):
    with open("blacklistpermissions.json", "r+") as file:
        try:
            entries = json.load(file)
        except json.decoder.JSONDecodeError:
            entries = []

        # Überprüfen, ob es bereits einen Eintrag mit der gleichen Guild-ID gibt
        existing_entry = next((entry for entry in entries if entry["guild_id"] == ctx.guild.id), None)

        # Wenn vorhandener Eintrag gefunden wird, löschen und ersetzen
        if existing_entry:
            existing_entry["role_id"] = role.id
        else:
            # Neuen Eintrag hinzufügen
            new_entry = {"guild_id": ctx.guild.id, "role_id": role.id}
            entries.append(new_entry)

        # JSON-Datei aktualisieren
        file.seek(0)
        file.truncate()
        json.dump(entries, file, indent=4)

    await ctx.respond(f"Die Rolle {role.mention} wurde für die Blacklist Verwaltung des Servers {ctx.guild.name} gespeichert.")

@set_required_role.error
async def set_required_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.respond("Nur Admins können diesen Befehl nutzen.")



@bot.slash_command(description="Entfernt die Rollen-ID für die Blacklist-Permissions.")
async def remove_required_role(ctx):
    with open("blacklistpermissions.json", "r+") as file:
        try:
            entries = json.load(file)
        except json.decoder.JSONDecodeError:
            entries = []

        # Überprüfen, ob es bereits einen Eintrag mit der gleichen Guild-ID gibt
        existing_entry = next((entry for entry in entries if entry["guild_id"] == ctx.guild.id), None)

        # Wenn vorhandener Eintrag gefunden wird, löschen
        if existing_entry:
            removed_role_id = existing_entry["role_id"]
            entries.remove(existing_entry)

            # JSON-Datei aktualisieren
            file.seek(0)
            file.truncate()
            json.dump(entries, file, indent=4)

            role = ctx.guild.get_role(removed_role_id)
            await ctx.respond(
                f"Die Blacklist-Rechte für die Rolle {role.name} auf dem Server {ctx.guild.name} wurde erfolgreich entfernt.")
        else:
            await ctx.respond("Bitte bestimme erst eine Rolle für die Blacklist.")















@bot.slash_command(description="Zeigt die Rolle für die Blacklist-Permissions an.")
async def get_required_role(ctx):
    with open("blacklistpermissions.json", "r") as file:
        try:
            entries = json.load(file)
        except json.decoder.JSONDecodeError:
            entries = []
        for entry in entries:
            if entry["guild_id"] == ctx.guild.id:
                role_id = entry["role_id"]
                role_name = await get_role_name(ctx.guild, role_id)
                await ctx.respond(
                    f"Die Rolle, zum bearbeiten der Blacklist auf {ctx.guild.name}  lautet: {role_name}")
                return
        await ctx.respond(f"Es wurde keine Blacklist Rolle für den Server {ctx.guild.name} definiert. Bitte bestimme erst eine Rolle für die Blacklist.")


def is_user_authorized(user_roles, guild):
    authorized_roles = ["Admin"]
    return any(role.name in authorized_roles for role in user_roles) or guild.owner == ctx.author


@bot.slash_command(description="Füge eine ID zur Blacklist hinzu")
async def füge_zur_blacklist_hinzu(ctx, id: int, name: str = None, grund: str = None):
    try:
        with open('blacklistpermissions.json') as f:
            json_data = f.read()
            if not json_data.strip():
                await ctx.respond("Fehler: Die Blacklist-Datei ist leer. Bitte fügen Sie mindestens eine Rolle hinzu.")
                return

            permissions = json.loads(json_data)

            if not is_user_authorized(ctx.author.roles, ctx.guild):
                await ctx.respond("Du hast keine Berechtigung, diese Aktion auszuführen.")
                return

            if len(str(id)) != 9:
                await ctx.respond("Ungültige ID. Eine gültige SWGOH-Benutzer-ID besteht aus 9 Ziffern.")
                return

            # Code for adding a new entry to the blacklist here ...

    except FileNotFoundError:
        await ctx.respond(
            "Fehler: Die Blacklist-Datei wurde nicht gefunden. Bitte fügen Sie mindestens eine Rolle hinzu.")

    if len(str(id)) != 9:
        await ctx.respond("Die SWGOH-ID muss 9 Zeichen haben.")
        return

    if not str(id).isdigit():
        await ctx.respond("Die ID muss eine numerische Zahl sein.")
        return

    if name and len(name) > 20:
        await ctx.respond("Der Name darf maximal 20 Zeichen haben.")
        return

    if grund and len(grund) > 20:
        await ctx.respond("Der Grund darf maximal 20 Zeichen haben.")
        return

    if is_blacklisted(id):
        await ctx.respond("Diese ID ist bereits in der Blacklist.")
    else:
        author_name = ctx.author.name  # Benutzername des Autors
        entry = {"id": id, "name": name, "grund": grund, "eingetragen_von": author_name}
        blacklist.append(entry)
        save_blacklist()  # Blacklist speichern
        response = f"Die ID ***{id}*** wurde zur Blacklist hinzugefügt."
        response += f"\nEingetragen von: {author_name}"
        if name:
            response += f"\nName: {name}"
        else:
            response += "\nName: [Optional]"
        if grund:
            response += f"\nGrund: {grund}"
        else:
            response += "\nGrund: [Optional]"
        await ctx.respond(response,)


@bot.slash_command(description="Entferne einen Eintrag aus der Blacklist.")
async def entferne_eintrag_aus_blacklist(ctx, entry_number: int):
    try:
        with open('blacklistpermissions.json') as f:
            json_data = f.read()
            if not json_data.strip():
                await ctx.respond("Fehler: Die Blacklist-Datei ist leer. Bitte fügen Sie mindestens eine Rolle hinzu.")
                return

            permissions = json.loads(json_data)

            if not is_user_authorized(ctx.author.roles, ctx.guild):
                await ctx.respond("Du hast keine Berechtigung, diese Aktion auszuführen.")
                return

            with open('blacklist.json') as f:
                json_data = f.read()
                if not json_data.strip():
                    await ctx.respond("Die Blacklist ist leer. Es gibt nichts zu entfernen.")
                    return

                blacklist = json.loads(json_data)

            if entry_number > 0 and entry_number <= len(blacklist):
                entry = blacklist.pop(entry_number - 1)
                save_blacklist()  # Blacklist speichern
                await ctx.respond(f"Eintrag {entry_number} (ID: {entry['id']}) wurde aus der Blacklist entfernt.")
            else:
                await ctx.respond("Ungültige Nummer. Bitte gib eine gültige fortlaufende Nummer an.")

    except FileNotFoundError:
        await ctx.respond(
            "Fehler: Die Blacklist-Datei wurde nicht gefunden. Bitte fügen Sie mindestens eine Rolle hinzu.")


@bot.slash_command(description="Frage die IDs in der Blacklist ab")
async def zeige_blacklist(ctx):
    if blacklist:
        embed = discord.Embed(title="Blacklist ☠️", color=0xFF0000)

        # Berechne die maximale Länge für jede Spalte basierend auf den Werten in der Blacklist
        max_id_length = max(len(str(entry["id"])) for entry in blacklist)
        max_name_length = max(len(entry["name"] or "") for entry in blacklist)
        max_grund_length = max(len(entry["grund"] or "") for entry in blacklist)
        max_eingetragen_von_length = max(len(entry["eingetragen_von"]) for entry in blacklist)

        # Erstelle eine Tabelle mit dynamischen Spaltenbreiten
        table = "Nr.  | ID" + " " * (max_id_length - 2) + " | Name" + " " * (max_name_length - 4) + " | Grund" + " " * (
                    max_grund_length - 5) + " | Eingetragen von" + " " * (max_eingetragen_von_length - 13) + "\n"
        table += "-" * (6 + max_id_length + max_name_length + max_grund_length + max_eingetragen_von_length) + "\n"

        # Enumerate über die Einträge, um die Nummerierung zu erstellen
        for index, entry in enumerate(blacklist, start=1):
            id = str(entry["id"]).ljust(max_id_length)
            name = (entry["name"] or "").ljust(max_name_length)
            grund = (entry["grund"] or "").ljust(max_grund_length)
            eingetragen_von = entry["eingetragen_von"].ljust(max_eingetragen_von_length)

            # Füge einen Eintrag zur Tabelle hinzu
            table += f"{index:<4}| {id} | {name} | {grund} | {eingetragen_von}\n"

        # Füge die Tabelle als ein Feld zum Embed hinzu
        embed.add_field(name="Blacklist Einträge", value="```" + table + "```", inline=False)

        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title="Blacklist ☠️", description="Die Blacklist ist leer.", color=0x00FF00)
        await ctx.respond(embed=embed)


@bot.slash_command(
    description="Extrahiere den Spielername aus einer SWGoH-Profilseite und gleiche mit der Blacklist ab")
async def durchsuche_profil(ctx, url: str):
    player_id = extract_player_id(url)
    player_name = extract_player_name(url)

    if player_id and player_name:
        if is_blacklisted(player_id):
            await ctx.respond(
                f"Der Spieler mit der ID **{player_id}** und dem Namen **{player_name}** ist auf der Blacklist.")
        else:
            await ctx.respond(
                f"Der Spieler mit der ID **{player_id}** und dem Namen **{player_name}** ist nicht auf der Blacklist.")
    else:
        await ctx.respond("Ungültige URL. Das SWGoH-Profil konnte nicht durchsucht werden.")


def is_blacklisted(player_id):
    return any(str(entry["id"]) == str(player_id) for entry in blacklist)


def remove_entry_from_blacklist(id):
    global blacklist
    blacklist = [entry for entry in blacklist if entry["id"] != id]


def load_blacklist():
    global blacklist
    try:
        with open("blacklist.json", "r") as file:
            blacklist = json.load(file)
    except FileNotFoundError:
        blacklist = []


def extract_player_id(url):
    pattern = r"\/p\/(\d+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def extract_player_name(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        player_name_element = soup.find('h5', class_='panel-title text-center m-b-sm')
        if player_name_element:
            player_name = player_name_element.text.strip()
            return player_name
    return None


def is_blacklisted(player_id):
    return any(str(entry["id"]) == str(player_id) for entry in blacklist)


async def load_blacklist():
    global blacklist
    try:
        async with aiofiles.open("blacklist.json", "r") as file:
            blacklist = json.loads(await file.read())
    except FileNotFoundError:
        blacklist = []
    except json.decoder.JSONDecodeError:
        blacklist = []


def is_user_authorized(roles, guild):
    with open("blacklistpermissions.json", "r") as file:
        entries = json.load(file)
        for entry in entries:
            if entry["guild_id"] == guild.id:
                role_id = entry["role_id"]
                role = guild.get_role(role_id)
                if role and role in roles:
                    return True
    return False


def save_blacklist():
    with open('blacklist.json', 'w') as f:
        json.dump(blacklist, f)

async def get_role_name(guild, role_id):
    role = guild.get_role(role_id)
    if role:
        return role.name
    else:
        return None
