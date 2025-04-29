import discord
from discord.ext import commands
from src.config import DISCORD_TOKEN
from src.memory_manager import initialize_firebase
from bot_utilities.commands import BotCommands # Importujeme naše příkazy

# Inicializace Firebase na začátku
if not initialize_firebase():
    print("Bot se nespustí kvůli chybě při inicializaci Firebase.")
    exit() # Ukončíme skript, pokud Firebase není připraveno

# Definice intentů - řekne Discordu, jaké události chceme poslouchat
# messages a message_content jsou nezbytné pro čtení zpráv
# guilds je potřeba pro získání informací o serverech
# voice_states je potřeba, pokud bys chtěl, aby se bot připojil do voice kanálu pro TTS (náročnější implementace)
intents = discord.Intents.default()
intents.message_content = True # Důležité pro čtení obsahu zpráv
intents.guilds = True # Pro informace o serverech
# intents.voice_states = True # Potřeba, pokud bot má mluvit ve voice kanálech (vyžaduje pokročilejší implementaci)

# Vytvoření instance bota
bot = commands.Bot(command_prefix="!", intents=intents) # Prefix ! zde není kritický, budeme používat hlavně slash příkazy

# Přidání cog s příkazy
async def setup_bot():
    await bot.add_cog(BotCommands(bot))
    print("Cog s příkazy přidán.")

# Událost při připravenosti bota (už máme v BotCommands on_ready, ale můžeš přidat další zde)
# @bot.event
# async def on_ready():
#    print(f'{bot.user} se připojil k Discordu!')
#    # V BotCommands.on_ready se provádí synchronizace příkazů a načítání dat z DB

# Spuštění bota
async def main():
    await setup_bot()
    if DISCORD_TOKEN:
        await bot.start(DISCORD_TOKEN)
    else:
        print("Chyba: Discord token není nastaven v .env souboru!")


if __name__ == "__main__":
    # Použití asyncio.run pro spuštění asynchronního kódu
    try:
        print("Spouštím bota...")
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot vypnut.")
    except Exception as e:
        print(f"Neočekávaná chyba při spuštění bota: {e}")