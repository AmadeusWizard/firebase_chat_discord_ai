import discord
from discord.ext import commands
from discord import app_commands
from src.memory_manager import load_active_channels, save_active_channels, load_conversation, save_conversation, add_message_to_conversation
from src.ai_chat import get_ai_response
from src.tts import get_tts_audio, cleanup_audio_file
from src.npc_manager import get_available_npcs, get_npc_prompt

# Načti aktivní kanály při startu modulu
active_channels = load_active_channels()
# Načti dostupné NPC při startu modulu
available_npcs = get_available_npcs()
# Zvol si výchozí NPC, pokud žádné není aktivní v kanálu
DEFAULT_NPC_ID = list(available_npcs.keys())[0] if available_npcs else "default" # Zvol první NPC nebo "default"

class BotCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Uložíme aktivní NPC pro každý kanál
        self.channel_npc = {} # {channel_id: npc_id}

    # Načtení aktivních kanálů a jejich NPC při spuštění bota
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Přihlášen jako {self.bot.user} (ID: {self.bot.user.id})')
        print('------')
        # Synchronizace slash příkazů - důležité pro jejich zobrazení na Discordu
        await self.bot.tree.sync()
        print("Slash příkazy synchronizovány.")

        # Načtení aktivních kanálů z databáze při startu
        global active_channels
        active_channels = load_active_channels()
        print(f"Načteny aktivní kanály: {active_channels}")

        # Zde bys mohl načíst i poslední aktivní NPC pro každý aktivní kanál z DB,
        # pokud to potřebuješ udržovat perzistentně. Pro jednoduchost teď použijeme výchozí.
        for channel_id in active_channels:
             # Zde by byla logika pro načtení preferovaného NPC pro daný kanál, pokud existuje
             self.channel_npc[channel_id] = DEFAULT_NPC_ID # Pro začátek použijeme výchozí

        print('Bot je připraven!')
        # Základní info o botovi (částečná implementace Dashboardu)
        print("\n--- Info o Botovi ---")
        print(f"ID bota: {self.bot.user.id}")
        print(f"Připojen na {len(self.bot.guilds)} serverech.")
        print(f"Aktivní v {len(active_channels)} kanálech (po načtení).")
        print(f"Dostupné NPC: {', '.join(available_npcs)}")
        print("----------------------")


    # Listener pro zpracování zpráv, když je bot aktivní v kanálu
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignoruj zprávy od samotného bota nebo od webhooků
        if message.author == self.bot.user or message.webhook_id is not None:
            return

        # Zkontroluj, zda je kanál aktivní a zda zpráva není slash příkaz
        if message.channel.id in active_channels and not message.content.startswith('/'):
            channel_id = message.channel.id
            user_id = message.author.id
            npc_id = self.channel_npc.get(channel_id, DEFAULT_NPC_ID) # Získej NPC pro kanál, jinak výchozí

            # Zkontroluj, zda existuje prompt pro vybrané NPC
            npc_prompt = get_npc_prompt(npc_id)
            if not npc_prompt:
                 await message.channel.send(f"Promiň, NPC s ID `{npc_id}` není definováno. Prosím, vyber jiné pomocí `/chat active <npc_id>`.")
                 return # Přestaň zpracovávat zprávu, pokud NPC neexistuje

            # Načti historii konverzace
            conversation_history = load_conversation(npc_id, channel_id, user_id)

            # Přidej systémovou zprávu s promptem NPC na začátek historie pro AI
            # OpenAI API a kompatibilní obvykle používají role: system, user, assistant
            if not conversation_history or conversation_history[0].get('role') != 'system':
                 # Přidáme prompt jen pokud už tam není nebo historie je prázdná
                 conversation_history.insert(0, {"role": "system", "content": npc_prompt})

            # Přidej aktuální zprávu uživatele do historie
            conversation_history.append({"role": "user", "content": message.content})

            # Zavolej AI pro odpověď (funkce už obsahuje indikátor psaní)
            ai_response_text = await get_ai_response(conversation_history, message.channel)

            if ai_response_text:
                # Přidej odpověď AI do historie konverzace
                conversation_history.append({"role": "assistant", "content": ai_response_text})

                # Ulož aktualizovanou konverzaci zpět do databáze
                # Můžeš ukládat po každé zprávě, nebo po celé interakci, nebo po určitém počtu zpráv
                # save_conversation(npc_id, channel_id, user_id, conversation_history) # Uloží celou historii (potenciálně velkou)
                # Lepší je možná průběžně přidávat zprávy, ale závisí na databázové struktuře a efektivitě zápisu
                # add_message_to_conversation(npc_id, channel_id, user_id, {"role": "user", "content": message.content}) # Příklad průběžného ukládání uživatelské zprávy
                # add_message_to_conversation(npc_id, channel_id, user_id, {"role": "assistant", "content": ai_response_text}) # Příklad průběžného ukládání AI odpovědi
                # Pro jednoduchost v tomto příkladu ukládáme celou historii po získání odpovědi, ale s omezením délky při načítání.
                # Zde provedeme uložení celé (již omezené) historie po získání odpovědi.
                save_conversation(npc_id, channel_id, user_id, conversation_history)


                # Pošli odpověď AI na Discord
                await message.channel.send(ai_response_text)

                # Generuj a pošli TTS audio
                audio_file_path = await get_tts_audio(ai_response_text)
                if audio_file_path:
                    try:
                        # discord.File vyžaduje lokální cestu k souboru
                        audio_file = discord.File(audio_file_path)
                        # Pošli audio soubor jako přílohu
                        await message.channel.send(file=audio_file)
                    except Exception as e:
                        print(f"Chyba při posílání audio souboru: {e}")
                    finally:
                        # Uklid dočasného audio souboru
                        cleanup_audio_file(audio_file_path)


    # Slash příkaz /ping
    @app_commands.command(name="ping", description="Zkontroluje odezvu bota.")
    async def ping_command(self, interaction: discord.Interaction):
        # 'Graphický' design pro konzolového bota bude prostě hezky formátovaný text
        latency_ms = round(self.bot.latency * 1000, 2)
        response_text = f"```Pong! 🏓\nOdezva bota: {latency_ms} ms```"
        await interaction.response.send_message(response_text, ephemeral=False) # ephemeral=True by zprávu zobrazil jen uživateli, který příkaz použil


    # Slash příkaz /chat active/deactivate
    @app_commands.command(name="chat", description="Aktivuje/deaktivuje AI chat bota v tomto kanálu a volitelně nastaví NPC.")
    @app_commands.describe(action="Vyber 'active' nebo 'deactivate'.", npc_id="Volitelné: ID NPC pro aktivaci. Nechej prázdné pro výchozí.")
    @app_commands.choices(action=[
        discord.app_commands.Choice(name="active", value="active"),
        discord.app_commands.Choice(name="deactivate", value="deactivate")
    ])
    async def chat_command(self, interaction: discord.Interaction, action: discord.app_commands.Choice[str], npc_id: str = None):
        channel_id = interaction.channel_id

        if action.value == "active":
            if channel_id in active_channels:
                 response_text = f"AI chat je již v tomto kanálu aktivní."
                 # Pokud bylo zadáno NPC, zkusíme ho nastavit
                 if npc_id:
                      if npc_id in available_npcs:
                           self.channel_npc[channel_id] = npc_id
                           response_text += f" Bylo nastaveno NPC: **{npc_id}**."
                           # Můžeš zde uložit preferované NPC pro kanál do DB, pokud chceš perzistenci
                      else:
                           response_text += f" NPC s ID `{npc_id}` neexistuje. Používá se aktuálně nastavené NPC ({self.channel_npc.get(channel_id, DEFAULT_NPC_ID)})."
                 else:
                      response_text += f" Používá se aktuální NPC ({self.channel_npc.get(channel_id, DEFAULT_NPC_ID)})."


            else:
                active_channels.add(channel_id)
                save_active_channels(active_channels) # Ulož změnu do DB
                response_text = f"AI chat byl v tomto kanálu **aktivován**."
                # Nastav NPC
                if npc_id and npc_id in available_npcs:
                     self.channel_npc[channel_id] = npc_id
                     response_text += f" Bylo nastaveno NPC: **{npc_id}**."
                else:
                    # Použij výchozí nebo aktuální pro kanál (pokud již existuje záznam)
                    if channel_id in self.channel_npc:
                         # Kanál byl neaktivní, ale měl nastavené NPC, použijeme ho
                         used_npc_id = self.channel_npc[channel_id]
                         response_text += f" Používá se dříve nastavené NPC: **{used_npc_id}**."
                    else:
                        # Kanál se aktivuje poprvé nebo neměl nastavené NPC, použijeme výchozí
                        self.channel_npc[channel_id] = DEFAULT_NPC_ID
                        response_text += f" Bylo nastaveno **výchozí** NPC: **{DEFAULT_NPC_ID}**."

                # Zde bys mohl uložit preferované NPC pro kanál do DB, pokud chceš perzistenci


        elif action.value == "deactivate":
            if channel_id in active_channels:
                active_channels.remove(channel_id)
                save_active_channels(active_channels) # Ulož změnu do DB
                response_text = f"AI chat byl v tomto kanálu **deaktivován**."
                # Můžeš zde zvážit smazání záznamu o preferovaném NPC pro kanál z DB, pokud chceš perzistenci
            else:
                response_text = f"AI chat není v tomto kanálu aktivní."

        await interaction.response.send_message(response_text, ephemeral=False)

    # Auto-complete pro npc_id v příkazu /chat active
    @chat_command.autocomplete('npc_id')
    async def chat_npc_autocomplete(self, interaction: discord.Interaction, current: str):
        # Nabídne dostupné NPC, které se shodují s tím, co uživatel píše
        return [
            app_commands.Choice(name=npc_id, value=npc_id)
            for npc_id in available_npcs if current.lower() in npc_id.lower()
        ][:25] # Omezíme počet nabídek na 25, limit Discordu


    # Zde bys mohl přidat další příkazy, např. pro zobrazení aktuálního NPC v kanálu, smazání paměti atd.
    @app_commands.command(name="current_npc", description="Zobrazí aktuálně aktivní NPC v tomto kanálu.")
    async def current_npc_command(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        if channel_id in active_channels:
            current_npc = self.channel_npc.get(channel_id, DEFAULT_NPC_ID)
            await interaction.response.send_message(f"Aktuálně aktivní NPC v tomto kanálu je: **{current_npc}**", ephemeral=False)
        else:
            await interaction.response.send_message("AI chat není v tomto kanálu aktivní.", ephemeral=False)

    @app_commands.command(name="list_npcs", description="Zobrazí seznam dostupných NPC.")
    async def list_npcs_command(self, interaction: discord.Interaction):
        if available_npcs:
            npc_list = ", ".join(available_npcs)
            await interaction.response.send_message(f"Dostupná NPC: {npc_list}", ephemeral=False)
        else:
            await interaction.response.send_message("Nebyly nalezeny žádné definice NPC v souboru NPC.txt.", ephemeral=False)

    # Příkaz pro smazání paměti pro aktuálního uživatele a NPC v kanálu (pro ladění nebo reset)
    @app_commands.command(name="reset_memory", description="Smaže paměť pro aktuální NPC a uživatele v tomto kanálu.")
    async def reset_memory_command(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        user_id = interaction.user.id
        npc_id = self.channel_npc.get(channel_id, DEFAULT_NPC_ID)

        try:
            ref = db.reference(f'{MEMORY_DB_PATH}/{npc_id}/{channel_id}/{user_id}')
            ref.set(None) # Nastavením na None se záznam smaže
            await interaction.response.send_message(f"Paměť pro NPC `{npc_id}` a uživatele **{interaction.user.display_name}** v tomto kanálu byla smazána.", ephemeral=False)
            print(f"Paměť smazána pro NPC {npc_id}, kanál {channel_id}, uživatele {user_id}") # Ladicí výpis
        except Exception as e:
            print(f"Chyba při mazání paměti: {e}")
            await interaction.response.send_message("Došlo k chybě při mazání paměti. 😥", ephemeral=False)