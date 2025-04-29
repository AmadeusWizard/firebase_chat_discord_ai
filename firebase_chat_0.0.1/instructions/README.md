# Discord AI Chat Bot s Pamětí a NPC

Tento projekt implementuje Discord bota v Pythonu s AI chatovacími funkcemi, perzistentní pamětí pomocí Firebase a systémem NPC (Non-Player Character).

## Funkce

* AI chat s kontextovou pamětí (uloženou ve Firebase).
* Systém NPC s definovatelnými prompty v souboru `NPC.txt`.
* Slash příkazy pro ovládání bota:
    * `/ping`: Zkontroluje odezvu bota.
    * `/chat active [npc_id]`: Aktivuje AI chat v aktuálním kanálu, volitelně nastaví konkrétní NPC.
    * `/chat deactivate`: Deaktivuje AI chat v aktuálním kanálu.
    * `/current_npc`: Zobrazí aktuálně aktivní NPC v kanálu.
    * `/list_npcs`: Zobrazí seznam dostupných NPC definovaných v `NPC.txt`.
    * `/reset_memory`: Smaže paměť konverzace pro aktuálního uživatele a NPC v kanálu.
* Integrace Text-to-Speech (TTS) pro čtení odpovědí AI nahlas (vyžaduje kompatibilní TTS API, např. OpenAI TTS).
* Indikátor psaní bota během generování odpovědi.
* Perzistentní ukládání aktivních kanálů do Firebase.

## Nastavení

1.  **Klonování repozitáře:**
    ```bash
    git clone <URL_TVÉHO_REPOZITÁŘE>
    cd <TVŮJ_NÁZEV_PROJEKTU>
    ```

2.  **Vytvoření virtuálního prostředí (doporučeno):**
    ```bash
    python -m venv venv
    # Na Windows:
    # venv\Scripts\activate
    # Na macOS/Linux:
    # source venv/bin/activate
    ```

3.  **Instalace závislostí:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Nastavení Discord Bota:**
    * Přejdi na [Discord Developer Portal](https://discord.com/developers/applications).
    * Vytvoř novou aplikaci.
    * Přejdi do sekce "Bot" a klikni "Add Bot".
    * Zkopíruj "TOKEN" - **nezdílej ho s nikým!**
    * V sekci "Bot" sjeď níže k "Privileged Gateway Intents" a zapni `PRESENCE INTENT`, `SERVER MEMBERS INTENT` a `MESSAGE CONTENT INTENT`. **`MESSAGE CONTENT INTENT` je nezbytný!**
    * Pozvi bota na svůj server. V sekci "OAuth2" -> "URL Generator" vyber `bot` a `applications.commands` jako `SCOPES`. V "BOT PERMISSIONS" vyber potřebná oprávnění, minimálně `Send Messages`, `Read Message History`, `Send Messages in Threads`. Pokud chceš používat TTS, budeš potřebovat i `Speak` a `Connect` ve voice kanálech (to vyžaduje pokročilejší implementaci vstupu do voice kanálu). Zkopíruj vygenerované URL a otevři ji v prohlížeči pro pozvání bota.

5.  **Nastavení Firebase:**
    * Přejdi na [Firebase Console](https://console.firebase.google.com/).
    * Vytvoř nový projekt.
    * V panelu navigace rozbal "Build" a vyber "Realtime Database". Vytvoř novou databázi (začni v testovacím režimu pro jednoduchost během vývoje).
    * V panelu navigace vyber "Project settings" (vedle "Project Overview"). Přejdi na záložku "Service accounts".
    * Klikni na "Generate new private key". Tím se stáhne JSON soubor s přihlašovacími údaji. **Neukládej tento soubor do repozitáře a zacházej s ním opatrně!** Ulož tento soubor na bezpečné místo na svém počítači.

6.  **Nastavení AI Chat a TTS API:**
    * Získej API endpoint a klíč pro tvůj AI chat model (`https://helixmind.online/v1/chat/completions`).
    * Získej API endpoint a klíč pro tvůj TTS model (pokud používáš jiný než ten integrovaný v chat API, např. OpenAI TTS).

7.  **Vytvoření souboru `.env`:**
    * V hlavním adresáři projektu vytvoř soubor s názvem `.env`.
    * Vyplň do něj údaje získané v předchozích krocích. **Nahraď zástupné hodnoty svými skutečnými údaji.**
    ```env
    DISCORD_TOKEN=TVUJ_DISCORD_BOT_TOKEN_Z_DISCORD_DEVELOPER_PORTAL
    CHAT_API_ENDPOINT=[https://helixmind.online/v1/chat/completions](https://helixmind.online/v1/chat/completions)
    CHAT_API_KEY=TVUJ_CHAT_API_KLIC  # Pokud tvůj endpoint vyžaduje klíč, jinak nech prázdné
    CHAT_MODEL=mai-ds-r1
    TTS_API_ENDPOINT=[https://api.openai.com/v1/audio/speech](https://api.openai.com/v1/audio/speech) # Příklad OpenAI TTS API
    TTS_API_KEY=TVUJ_OPENAI_API_KLIC # Klíč pro OpenAI TTS, pokud používáš jejich službu, jinak nech prázdné
    TTS_MODEL=gpt-4o-mini-tts
    TTS_VOICE=verse
    FIREBASE_CREDENTIALS_PATH=cesta/k/tvemu/firebase/sluzebnimu/kluci.json # **Absolutní nebo relativní cesta z místa spuštění skriptu** k JSON souboru s Firebase klíčem
    FIREBASE_DATABASE_URL=[https://TVUJ-PROJEKT-ID.firebaseio.com](https://TVUJ-PROJEKT-ID.firebaseio.com) # URL tvojí Firebase Realtime Database
    ACTIVE_CHANNELS_DB_PATH=active_channels # Cesta ve Firebase pro uložení aktivních kanálů (můžeš změnit)
    MEMORY_DB_PATH=conversations # Cesta ve Firebase pro uložení konverzačních dat (můžeš změnit)
    ```
    * **Důležité:** Ujisti se, že `FIREBASE_CREDENTIALS_PATH` je **správná cesta** k tvému JSON souboru s Firebase klíčem z místa, kde spouštíš `bot.py`.

8.  **Nastavení NPC:**
    * Uprav soubor `NPC/NPC.txt`. Každý řádek by měl obsahovat unikátní ID NPC, následované dvojtečkou a promptem pro toto NPC. Řádky začínající `#` jsou ignorovány.
    ```txt
    # Příklad:
    astronomer:Jsi přátelská a vášnivá astronomka jménem Stella...
    ```

## Spuštění Bota

Ujisti se, že máš aktivované virtuální prostředí (pokud jsi ho vytvořil) a že jsi v hlavním adresáři projektu.

```bash
python src/bot.py