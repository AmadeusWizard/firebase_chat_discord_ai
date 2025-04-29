import os

NPC_FILE_PATH = 'NPC/NPC.txt' # Cesta k souboru s NPC definicemi

def load_npcs():
    npcs = {}
    if not os.path.exists(NPC_FILE_PATH):
        print(f"Chyba: Soubor s NPC definicemi nenalezen: {NPC_FILE_PATH}")
        return npcs

    try:
        with open(NPC_FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split(':', 1)
                if len(parts) == 2:
                    npc_id = parts[0].strip()
                    npc_prompt = parts[1].strip()
                    npcs[npc_id] = {"prompt": npc_prompt}
                    # print(f"Načten NPC: {npc_id}") # Ladicí výpis
                else:
                    print(f"Upozornění: Přeskočen neplatný řádek v NPC.txt: {line}")

    except Exception as e:
        print(f"Chyba při načítání NPC souboru: {e}")

    if not npcs:
        print("Upozornění: V souboru NPC.txt nebyly nalezeny žádné platné NPC definice.")

    return npcs

# Globální proměnná pro uložení načtených NPC
LOADED_NPC = load_npcs()

def get_npc_prompt(npc_id: str):
    return LOADED_NPC.get(npc_id, {}).get("prompt")

def get_available_npcs():
    return LOADED_NPC.keys()