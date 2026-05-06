# Ship Survivors
I am adding to the AI slop by using Claude to remaster a game I made about 10 years ago with Java. 


A Python/pygame remake of a Java LibGDX game. Dodge and destroy rocks while switching between three weapons. Survive as long as you can.

## Play in the browser

The game is deployed via GitHub Pages using [Pygbag](https://pygame-web.github.io/).  
👉 **[Play here](https://walup.github.io/ship-survivors-remastered)**

> Note: first load may take a moment — music files are large WAVs.

## Run locally

**Requirements:** Python 3.11+

```bash
pip install pygame
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| W / S or ↑ / ↓ | Move ship |
| Space or Click | Fire current weapon |
| 1 / 2 / 3 | Switch weapon |
| M | Toggle music |
| Esc | Pause / unpause |

## Weapons

- **Arduino Pistol** — fast horizontal bullets
- **Football Cat** — lobbed parabolic shot, high damage
- **Heartbreaker** — three spreading half-hearts

## Rock types

| Type | Colour | Behaviour |
|------|--------|-----------|
| Normal | Brown | Standard |
| Fast | Orange | 1.85× speed, small rocks seek the ship |
| Armored | Steel blue | 2 HP, cracks on first hit |

## Project structure

```
main.py          — entry point (asyncio loop, Pygbag compatible)
settings.py      — constants (resolution, speeds, colours)
particles.py     — particle system
entities/
  ship.py        — player ship
  rock.py        — rock types & splitting logic
  projectile.py  — bullet, football, half-heart
screens/
  menu.py        — main menu
  gameplay.py    — game loop & wave system
  game_over.py   — game over screen
  story.py       — story slide show
ui/
  hud.py         — hearts, score, weapon cards
assets/          — all sprites, atlases, and audio
```

## Deploying to GitHub Pages

1. Push this repo to GitHub.
2. Go to **Settings → Pages → Source** and set it to **GitHub Actions**.
3. The workflow at `.github/workflows/deploy.yml` builds with Pygbag and deploys automatically on every push to `main`.
