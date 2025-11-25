import json
import os
import time
from datetime import datetime

# Mock functions to simulate bot environment
CLANS_FILE = "clans_test.json"
PLAYERS_DB_FILE = "players_db_test.json"
LINKS_FILE = "links_test.json"

def load_json(filename):
    if not os.path.exists(filename): return {}
    with open(filename, 'r') as f: return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f: json.dump(data, f, indent=4)

# Setup test data
def setup():
    # Links
    save_json(LINKS_FILE, {
        "KillerGT": "1001",
        "VictimGT": "1002"
    })
    
    # Clans
    save_json(CLANS_FILE, {
        "CLAN_A": {"leader": "1001", "members": []},
        "CLAN_B": {"leader": "1002", "members": []},
        "wars": {
            "war1": {
                "clan1": "CLAN_A",
                "clan2": "CLAN_B",
                "score": {"CLAN_A": 0, "CLAN_B": 0},
                "active": True,
                "start_time": datetime.now().isoformat(),
                "requester": "CLAN_A"
            }
        }
    })

def get_discord_id_by_gamertag(gt):
    links = load_json(LINKS_FILE)
    return links.get(gt)

def get_user_clan(user_id):
    clans = load_json(CLANS_FILE)
    uid = str(user_id)
    for tag, data in clans.items():
        if tag == "wars": continue
        if data.get("leader") == uid or uid in data.get("members", []):
            return tag, data
    return None, None

def update_war_score(killer_name, victim_name):
    killer_id = get_discord_id_by_gamertag(killer_name)
    victim_id = get_discord_id_by_gamertag(victim_name)
    
    if not killer_id or not victim_id:
        print("IDs not found")
        return None
        
    k_tag, k_clan = get_user_clan(killer_id)
    v_tag, v_clan = get_user_clan(victim_id)
    
    print(f"Killer Clan: {k_tag}, Victim Clan: {v_tag}")
    
    if not k_tag or not v_tag or k_tag == v_tag:
        print("Invalid clan match")
        return None
        
    clans = load_json(CLANS_FILE)
    wars = clans.get("wars", {})
    war_id = None
    
    for wid, wdata in wars.items():
        if not wdata.get("active"): continue
        participants = [wdata["clan1"], wdata["clan2"]]
        if k_tag in participants and v_tag in participants:
            war_id = wid
            break
            
    if war_id:
        wars[war_id]["score"][k_tag] += 1
        clans["wars"] = wars
        save_json(CLANS_FILE, clans)
        return wars[war_id]["score"]
    return None

# Run Test
setup()
print("Simulating kill: KillerGT (CLAN_A) kills VictimGT (CLAN_B)")
score = update_war_score("KillerGT", "VictimGT")

if score and score["CLAN_A"] == 1:
    print("SUCCESS: Score updated correctly!", score)
else:
    print("FAILURE: Score not updated.", score)

# Cleanup
try:
    os.remove(CLANS_FILE)
    os.remove(PLAYERS_DB_FILE)
    os.remove(LINKS_FILE)
except: pass
