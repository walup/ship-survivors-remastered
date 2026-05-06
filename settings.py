import os

ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

WIDTH, HEIGHT = 800, 450
FPS = 60
TITLE = "Ship Survivors"

SHIP_SPEED = 260
SHIP_X = 90

ROCK_SPEEDS = {'large': 90, 'medium': 115, 'small': 145}
ROCK_RADII = {'large': 72, 'medium': 46, 'small': 26}
ROCK_SPAWN_INTERVAL = 3.8
MAX_ROCKS = 6

PISTOL_COOLDOWN = 0.18
BULLET_SPEED = 620
FOOTBALL_SPEED = 340
HALFHEART_SPEED = 280

MAX_HEARTS = 3
HEART_PIECES = 4
HIT_IMMUNITY = 2.0

SCORE_LARGE = 80
SCORE_MEDIUM = 40
SCORE_SMALL = 20

WAVE_DURATION = 30.0   # seconds per wave

WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
RED     = (220,  55,  55)
GREEN   = (55,  200,  80)
BLUE    = (55,  120, 220)
YELLOW  = (255, 220,   0)
ORANGE  = (255, 140,   0)
GRAY    = (120, 120, 130)
DARK    = (20,  20,  30)
ACCENT  = (80,  200, 255)
