import json
from pathlib import Path
from datetime import datetime

MOOD_LOG_PATH = Path("data/mood_log.json")

def log_mood(feeling: str, note: str = ""):
    if not MOOD_LOG_PATH.exists():
        MOOD_LOG_PATH.write_text("[]")
    logs = json.loads(MOOD_LOG_PATH.read_text())
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "feeling": feeling,
        "note": note
    })
    MOOD_LOG_PATH.write_text(json.dumps(logs, indent=2))
