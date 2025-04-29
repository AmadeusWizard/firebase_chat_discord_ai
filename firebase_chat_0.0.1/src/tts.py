import requests
import os
import asyncio
from src.config import TTS_API_ENDPOINT, TTS_API_KEY, TTS_MODEL, TTS_VOICE

# Dočasná složka pro ukládání MP3 souborů
TEMP_AUDIO_DIR = "temp_audio"
if not os.path.exists(TEMP_AUDIO_DIR):
    os.makedirs(TEMP_AUDIO_DIR)

async def get_tts_audio(text: str):
    if not TTS_API_KEY or not TTS_API_ENDPOINT:
        print("TTS API klíč nebo endpoint není nastaven. Nelze generovat audio.")
        return None

    headers = {
        "Authorization": f"Bearer {TTS_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": TTS_MODEL,
        "input": text,
        "voice": TTS_VOICE,
        "response_format": "mp3" # Požadujeme MP3 formát
    }

    try:
        # Opět používáme synchronní requests v executoru pro jednoduchost
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(TTS_API_ENDPOINT, headers=headers, json=payload))

        response.raise_for_status() # Vyvolá chybu pro špatné HTTP statusy

        # Generuj unikátní název souboru pro dočasné uložení
        audio_file_path = os.path.join(TEMP_AUDIO_DIR, f"tts_{asyncio.get_event_loop().time()}.mp3")

        # Ulož odpověď do MP3 souboru
        with open(audio_file_path, 'wb') as f:
            f.write(response.content)

        # print(f"TTS audio uloženo do {audio_file_path}") # Ladicí výpis
        return audio_file_path

    except requests.exceptions.RequestException as e:
        print(f"Chyba při volání TTS API: {e}")
        return None
    except Exception as e:
        print(f"Neočekávaná chyba při získávání TTS audia: {e}")
        return None

# Funkce pro smazání dočasného audio souboru
def cleanup_audio_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            # print(f"Dočasný audio soubor smazán: {file_path}") # Ladicí výpis
    except Exception as e:
        print(f"Chyba při mazání audio souboru {file_path}: {e}")