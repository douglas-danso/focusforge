import time
from tqdm import tqdm

def start_timer(minutes=25):
    seconds = minutes * 60
    print(f"⏳ Starting {minutes}-minute focus session...")
    for _ in tqdm(range(seconds), desc="Focus", ncols=70):
        time.sleep(1)
    print("\n✅ Pomodoro session complete!")
