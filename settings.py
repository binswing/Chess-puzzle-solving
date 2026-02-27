import json
import os

# --- Configuration ---
BOARD_ROWS = 8
BOARD_COLS = 8
SEARCH_ANIMATION = True
PLAY_ANIMATION_DURATION = 300
SEARCH_ANIMATION_DURATION = 10
PLAY_SPEED_LIMIT = (50, 1000)
SEARCH_SPEED_LIMIT = (0, 100)
FPS_LIMIT = (30, 240)

# Colors
COLOR_LIGHT = (235, 236, 208)
COLOR_DARK = (119, 149, 86)
COLOR_BG = (37, 37, 37) 
COLOR_HIGHLIGHT = (255, 255, 0, 100) 
COLOR_ORANGE_HIGHLIGHT = (179, 128, 0, 200)

# Graphic 
FPS = 120

# --- ASSETS PATH ---
APP_IMG_URL = "assets/images/app/"
PIECES_IMG_URL = "assets/images/pieces/"
DATA_URL = "data/"
SETTINGS_FILE = DATA_URL + "user_settings.json"

def load_settings():
    global SEARCH_ANIMATION, PLAY_ANIMATION_DURATION, SEARCH_ANIMATION_DURATION, FPS
    
    if not os.path.exists(DATA_URL):
        os.makedirs(DATA_URL)

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                SEARCH_ANIMATION = data.get("search_animation", SEARCH_ANIMATION)
                PLAY_ANIMATION_DURATION = data.get("play_anim_duration", PLAY_ANIMATION_DURATION)
                SEARCH_ANIMATION_DURATION = data.get("search_anim_duration", SEARCH_ANIMATION_DURATION)
                FPS = data.get("fps", FPS)
        except:
            print("Error loading settings, using defaults.")
            save_settings()
    else:
        save_settings()

def save_settings():
    data = {
        "search_animation": SEARCH_ANIMATION,
        "play_anim_duration": PLAY_ANIMATION_DURATION,
        "search_anim_duration": SEARCH_ANIMATION_DURATION,
        "fps": FPS
    }
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

load_settings()