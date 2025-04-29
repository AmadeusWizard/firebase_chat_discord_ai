import requests
import discord
import asyncio
from src.config import CHAT_API_ENDPOINT, CHAT_API_KEY, CHAT_MODEL

# Funkce pro poslání konverzace na chat API
async def get_ai_response(conversation_history: list, typing_channel: discord.TextChannel):
    # Příklad struktury pro OpenAI-kompatibilní API
    # Tvůj konkrétní endpoint může vyžadovat jinou strukturu
    headers = {
        "Content-Type": "application/json",
    }
    # Přidáme API klíč, pokud je definován
    if CHAT_API_KEY:
        headers["Authorization"] = f"Bearer {CHAT_API_KEY}"

    payload = {
        "model": CHAT_MODEL,
        "messages": conversation_history,
        # Můžeš přidat další parametry jako temperature, max_tokens atd.
        # "temperature": 0.7,
        # "max_tokens": 150,
    }

    # Aktivuj indikátor psaní v kanálu
    async with typing_channel.typing():
        try:
            # Využijeme asyncio pro neblokující volání requests v aiohttp,
            # ale pro jednoduchost zde použijeme synchronní requests.
            # Pro produkční bot by bylo lepší použít aiohttp pro asynchronní volání.
            # Ale teď to uděláme s requests, bude to jednodušší na pochopení.
            # POZOR: requests blokuje asyncio event loop! Pro produkci použij aiohttp.
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.post(CHAT_API_ENDPOINT, headers=headers, json=payload))

            response.raise_for_status() # Vyvolá chybu pro špatné HTTP statusy

            data = response.json()
            # Zpracování odpovědi - opět, struktura závisí na tvém API
            # Předpokládáme strukturu podobnou OpenAI:
            if data and data.get('choices'):
                ai_message = data['choices'][0]['message']
                return ai_message.get('content', '').strip()
            else:
                print(f"API odpovědělo nečekanou strukturou: {data}")
                return "Promiň, nedokázala jsem teď zpracovat odpověď od AI. 😞"

        except requests.exceptions.RequestException as e:
            print(f"Chyba při volání Chat API: {e}")
            return "Promiň, došlo k chybě při komunikaci s AI. 😞"
        except Exception as e:
            print(f"Neočekávaná chyba při získávání AI odpovědi: {e}")
            return "Ups, stala se nějaká neočekávaná chyba. 😥"
    # Indikátor psaní se automaticky vypne po opuštění 'async with' bloku