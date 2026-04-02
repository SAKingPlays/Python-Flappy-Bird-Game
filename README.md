# 🐦 Flappy Bird – Professional Pygame Edition

A clean, production-quality reimplementation of Flappy Bird in Python + Pygame.
Zero external assets needed – all graphics and sounds are generated procedurally.

---

## Requirements

| Package   | Version  |
|-----------|----------|
| Python    | ≥ 3.10   |
| pygame    | ≥ 2.1    |
| numpy     | ≥ 1.21 *(optional – enables sound effects)* |

Install dependencies:

```bash
pip install pygame numpy
```

---

## Running the Game

```bash
cd flappy_bird
python main.py
```

---

## Controls

| Key / Input        | Action                  |
|--------------------|-------------------------|
| **Space**          | Flap / Start / Restart  |
| **Left-click**     | Flap / Start / Restart  |
| **P** or **Esc**   | Pause / Resume          |
| **Q**              | Quit                    |

---

## Project Structure

```
flappy_bird/
├── main.py          Entry point – initialises pygame, runs Game
├── settings.py      All constants and configuration (edit here to tune gameplay)
├── game.py          State machine: MENU → PLAYING → PAUSED / GAME_OVER
├── bird.py          Bird sprite – physics, rotation, wing animation
├── pipe.py          PipePair sprite + PipeManager (spawning, difficulty ramp)
├── background.py    Multi-layer parallax: sky, mountains, clouds, ground
├── particles.py     Lightweight particle system (flap puffs, crash burst)
├── assets.py        Procedural asset generation – sprites, fonts, sounds
├── ui.py            All draw calls for HUD, menus, overlays, transitions
├── highscore.py     JSON-based high-score persistence
└── data/
    └── highscore.json   Created automatically on first play
```

---

## Gameplay Features

- **Smooth physics** – gravity, terminal velocity, exponential rotation smoothing
- **Wing animation** – 3-frame sprite cycle, rapid flap + slow idle modes
- **Parallax background** – 4 scrolling layers at independent speeds
- **Particle effects** – feather puffs on flap; explosive burst on crash
- **Screen shake** – decaying camera shake on collision
- **Difficulty scaling** – pipe speed and spawn rate increase every 5 points
- **Persistent high score** – saved to `data/highscore.json`
- **Grade system** – C / B / A / S medals on the game-over screen
- **Sound effects** – synthetically generated flap, score, hit, die sounds (requires numpy)
- **Pause / Resume** – full pause overlay without interrupting background

---

## Tuning the Game

All numeric constants live in `settings.py`.  Common tweaks:

```python
GRAVITY           = 0.38    # higher → harder
JUMP_VELOCITY     = -8.5    # more negative → higher jump
PIPE_GAP          = 175     # smaller → tighter gaps
PIPE_SPEED_INITIAL = 3.0    # higher → faster start
PIPE_SPEED_MAX    = 6.0     # cap on pipe velocity
SCORE_PER_DIFFICULTY_STEP = 5  # how often difficulty increases
```

---

## Suggested Further Improvements

### Art & Animation
- [ ] Load real PNG sprite sheets (swap generation functions in `assets.py`)
- [ ] Add a death spin/tumble animation for the bird
- [ ] Add animated water / river in the background
- [ ] Day → night colour-cycle over time

### Gameplay
- [ ] Power-ups (slow-motion, shield, score multiplier)
- [ ] Multiple bird skins with an unlock system
- [ ] Leaderboard (local SQLite or online via a simple REST API)
- [ ] Endless mode vs timed challenge mode

### Technical
- [ ] `asyncio`-based online multiplayer (race another bird)
- [ ] Gamepad / joystick support via `pygame.joystick`
- [ ] Replay system – record inputs, play back ghost runs
- [ ] In-game settings menu (volume, difficulty preset)
- [ ] Unit tests for physics and collision logic (`pytest`)
- [ ] PyInstaller packaging for distributable executables

### Audio
- [ ] Load real WAV / OGG files for richer sound
- [ ] Background music loop with pygame.mixer.music
- [ ] Dynamic audio (pitch-shift on near-miss)
