import json
from pathlib import Path

STORE_PATH = Path("data/store.json")
USER_PROFILE = Path("data/user_profile.json")

def load_store():
    if not STORE_PATH.exists():
        STORE_PATH.write_text(json.dumps({
            "Snack Break": {"cost": 20, "type": "break"},
            "Gaming Time (30m)": {"cost": 50, "type": "entertainment"},
            "Nap Time (20m)": {"cost": 30, "type": "rest"}
        }))
    return json.loads(STORE_PATH.read_text())

def load_profile():
    if not USER_PROFILE.exists():
        USER_PROFILE.write_text(json.dumps({"currency": 0, "purchases": []}))
    return json.loads(USER_PROFILE.read_text())

def save_profile(profile):
    USER_PROFILE.write_text(json.dumps(profile, indent=2))

def add_currency(amount):
    profile = load_profile()
    profile["currency"] += amount
    save_profile(profile)

def purchase_item(item_name):
    store = load_store()
    profile = load_profile()
    item = store.get(item_name)

    if not item:
        return "Item not found."
    if profile["currency"] < item["cost"]:
        return "Not enough points."

    profile["currency"] -= item["cost"]
    profile["purchases"].append(item_name)
    save_profile(profile)
    return f"Purchased: {item_name}"
