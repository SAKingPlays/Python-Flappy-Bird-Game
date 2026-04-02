"""
settings.py – Centralised game configuration.
All tuneable constants live here; nothing else imports between modules
at the constant level, keeping dependencies clean.
"""
from enum import Enum, auto


# ─── Game States ─────────────────────────────────────────────────────────────

class GameState(Enum):
    """All possible states the game state-machine can be in."""
    MENU      = auto()
    PLAYING   = auto()
    PAUSED    = auto()
    GAME_OVER = auto()


# ─── Display ─────────────────────────────────────────────────────────────────

SCREEN_WIDTH:  int = 400
SCREEN_HEIGHT: int = 600
FPS:           int = 60
TITLE:         str = "Flappy Bird"

# ─── Physics ─────────────────────────────────────────────────────────────────

GRAVITY:           float = 0.38
JUMP_VELOCITY:     float = -8.5
TERMINAL_VELOCITY: float = 14.0

# ─── Bird ────────────────────────────────────────────────────────────────────

BIRD_X:          int   = 85           # fixed horizontal position
BIRD_RADIUS:     int   = 17           # collision radius (slightly smaller than sprite)
BIRD_FRAME_COUNT: int  = 3            # wing animation frames

# ─── Pipes ───────────────────────────────────────────────────────────────────

PIPE_WIDTH:              int   = 68
PIPE_GAP:                int   = 175
PIPE_MIN_HEIGHT:         int   = 70   # min px for top pipe
PIPE_SPEED_INITIAL:      float = 3.0
PIPE_SPEED_MAX:          float = 6.0
PIPE_SPEED_INCREMENT:    float = 0.00025  # added every game tick
PIPE_SPAWN_INTERVAL_MS:  int   = 1500     # ms between spawns (initial)
PIPE_SPAWN_INTERVAL_MIN: int   = 900

# ─── Ground ──────────────────────────────────────────────────────────────────

GROUND_HEIGHT: int   = 22
GROUND_SPEED:  float = 3.0   # matches initial pipe speed

# ─── Difficulty ──────────────────────────────────────────────────────────────

SCORE_PER_DIFFICULTY_STEP: int = 5   # every N points the game gets harder

# ─── Screen Shake ────────────────────────────────────────────────────────────

SHAKE_INTENSITY: int   = 8
SHAKE_DURATION:  int   = 22   # frames

# ─── Particles ───────────────────────────────────────────────────────────────

FLAP_PARTICLE_COUNT:  int = 7
CRASH_PARTICLE_COUNT: int = 40
PARTICLE_GRAVITY:   float = 0.18

# ─── File Paths ──────────────────────────────────────────────────────────────

HIGHSCORE_FILE: str = "data/highscore.json"

# ─── Fonts ───────────────────────────────────────────────────────────────────

FONT_HUGE:   int = 54
FONT_LARGE:  int = 38
FONT_MEDIUM: int = 26
FONT_SMALL:  int = 19
FONT_TINY:   int = 14

# ─── Colours ─────────────────────────────────────────────────────────────────

# Sky
SKY_TOP    = (72,  160, 235)
SKY_BOTTOM = (28,  105, 200)

# Environment
GROUND_LIGHT   = (215, 185, 120)
GROUND_DARK    = (160, 118,  55)
GRASS_COLOR    = ( 88, 175,  60)
MOUNTAIN_FAR   = (155, 175, 192)
MOUNTAIN_NEAR  = ( 95, 135,  90)
CLOUD_COLOR    = (240, 248, 255)
CLOUD_SHADOW   = (210, 225, 240)

# Pipes
PIPE_BODY  = ( 84, 190,  75)
PIPE_DARK  = ( 50, 145,  50)
PIPE_LIGHT = (140, 215, 125)
PIPE_CAP   = ( 68, 175,  60)

# Bird
BIRD_YELLOW  = (255, 222,  45)
BIRD_GOLD    = (240, 185,  20)
BIRD_ORANGE  = (255, 155,   0)
BIRD_WHITE   = (255, 255, 255)
BIRD_DARK    = ( 55,  40,  10)

# UI
WHITE        = (255, 255, 255)
BLACK        = (  0,   0,   0)
SHADOW_COLOR = ( 25,  25,  25)
SCORE_GOLD   = (255, 215,   0)
GOLD_MEDAL   = (255, 200,  50)
SILVER_MEDAL = (192, 192, 192)
BRONZE_MEDAL = (200, 130,  50)
PANEL_BG     = ( 42,  42,  42, 200)   # RGBA
OVERLAY_CLR  = (  0,   0,   0)

# Particles
PARTICLE_FLAP_COLORS  = [(255, 255, 190), (255, 230,  90), (255, 190,  50)]
PARTICLE_CRASH_COLORS = [(255,  80,  40), (255, 160,  50), (255, 210,  80), (200, 200, 200)]
