import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHAT_API_ENDPOINT = os.getenv('CHAT_API_ENDPOINT')
CHAT_API_KEY = os.getenv('CHAT_API_KEY')
CHAT_MODEL = os.getenv('CHAT_MODEL')
TTS_API_ENDPOINT = os.getenv('TTS_API_ENDPOINT')
TTS_API_KEY = os.getenv('TTS_API_KEY')
TTS_MODEL = os.getenv('TTS_MODEL')
TTS_VOICE = os.getenv('TTS_VOICE')
FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')
FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')
ACTIVE_CHANNELS_DB_PATH = os.getenv('ACTIVE_CHANNELS_DB_PATH')
MEMORY_DB_PATH = os.getenv('MEMORY_DB_PATH')

# Kontrola, zda jsou všechny potřebné proměnné načteny
if not all([DISCORD_TOKEN, CHAT_API_ENDPOINT, CHAT_MODEL, FIREBASE_CREDENTIALS_PATH, FIREBASE_DATABASE_URL]):
    print("Chyba: Některé potřebné proměnné prostředí nejsou nastaveny!")
    # Můžeš zde vyvolat chybu nebo ukončit program
    # raise EnvironmentError("Některé potřebné proměnné prostředí nejsou nastaveny")