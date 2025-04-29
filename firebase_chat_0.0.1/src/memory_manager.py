import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
import json
from src.config import FIREBASE_CREDENTIALS_PATH, FIREBASE_DATABASE_URL, MEMORY_DB_PATH, ACTIVE_CHANNELS_DB_PATH

# Inicializace Firebase (provádí se jen jednou při startu bota)
def initialize_firebase():
    if not firebase_admin._apps:
        # Ujisti se, že cesta ke credentials souboru je správná a soubor existuje
        if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
            print(f"Chyba: Soubor s Firebase credentials nenalezen na cestě: {FIREBASE_CREDENTIALS_PATH}")
            # Zde bys měl ukončit bota nebo vyvolat chybu
            return False

        try:
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred, {
                'databaseURL': FIREBASE_DATABASE_URL
            })
            print("Firebase inicializováno úspěšně!")
            return True
        except Exception as e:
            print(f"Chyba při inicializaci Firebase: {e}")
            return False
    return True # Již inicializováno

# Funkce pro uložení konverzace
def save_conversation(npc_id: str, channel_id: int, user_id: int, conversation: list):
    try:
        ref = db.reference(f'{MEMORY_DB_PATH}/{npc_id}/{channel_id}/{user_id}')
        ref.set(conversation)
        # print(f"Konverzace pro NPC {npc_id}, kanál {channel_id}, uživatele {user_id} uložena.") # Ladicí výpis
    except Exception as e:
        print(f"Chyba při ukládání konverzace: {e}")

# Funkce pro načtení konverzace
def load_conversation(npc_id: str, channel_id: int, user_id: int, max_history_length: int = 20):
    try:
        ref = db.reference(f'{MEMORY_DB_PATH}/{npc_id}/{channel_id}/{user_id}')
        conversation = ref.get()
        if conversation is None:
            return []
        # Omezíme délku historie, aby zprávy pro AI nebyly moc dlouhé
        return conversation[-max_history_length:] # Vezmeme posledních N zpráv
    except Exception as e:
        print(f"Chyba při načítání konverzace: {e}")
        return []

# Funkce pro uložení aktivních kanálů
def save_active_channels(active_channels: set):
    try:
        ref = db.reference(ACTIVE_CHANNELS_DB_PATH)
        # Firebase nemá přímou podporu pro set, uložíme jako seznam
        ref.set(list(active_channels))
        print("Aktivní kanály uloženy.")
    except Exception as e:
        print(f"Chyba při ukládání aktivních kanálů: {e}")

# Funkce pro načtení aktivních kanálů
def load_active_channels():
    try:
        ref = db.reference(ACTIVE_CHANNELS_DB_PATH)
        channels_list = ref.get()
        if channels_list is None:
            return set()
        # Přepočítáme seznam na set
        return set(channels_list)
    except Exception as e:
        print(f"Chyba při načítání aktivních kanálů: {e}")
        return set()

# Funkce pro přidání zprávy do konverzace (pro průběžné ukládání) - Volitelné, lze ukládat i po každé interakci
def add_message_to_conversation(npc_id: str, channel_id: int, user_id: int, message: dict):
     try:
        ref = db.reference(f'{MEMORY_DB_PATH}/{npc_id}/{channel_id}/{user_id}')
        # Načteme aktuální konverzaci, přidáme zprávu a uložíme zpět.
        # Toto je méně efektivní pro časté zprávy, lepší může být načíst na začátku interakce a uložit na konci.
        # Pro jednoduchost zde ukážeme append. Pro produkční použití zvaž jinou strategii.
        conversation = ref.get()
        if conversation is None:
            conversation = []
        conversation.append(message)
        ref.set(conversation) # Uložení celé aktualizované konverzace
     except Exception as e:
         print(f"Chyba při přidávání zprávy do konverzace: {e}")