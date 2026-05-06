"""Ship Survivors — Python/pygame remake."""
import asyncio
import os, json, sys
import pygame
import settings as S
from screens.menu       import MenuScreen
from screens.gameplay   import GameplayScreen
from screens.game_over  import GameOverScreen
from screens.story      import StoryScreen

SAVE_FILE = os.path.join(os.path.dirname(__file__), 'save.json')


def load_high_score() -> int:
    try:
        with open(SAVE_FILE) as f:
            return json.load(f).get('high_score', 0)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return 0


def save_high_score(score: int):
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump({'high_score': score}, f)
    except OSError:
        pass  # silently skip in read-only environments (e.g. browser)


def load_image(path, fallback_size=(64, 64), fallback_color=(200, 100, 50)) -> pygame.Surface:
    if os.path.exists(path):
        return pygame.image.load(path).convert_alpha()
    surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf


def load_assets() -> dict:
    a = S.ASSETS
    assets = {}

    # Ship — crop from shipatlas.png
    ship_sheet = load_image(os.path.join(a, 'shipatlas.png'))
    assets['ship'] = ship_sheet.subsurface(pygame.Rect(2, 43, 313, 184))

    # Background (scale to screen height, preserve aspect ratio for seamless tiling)
    bg_path = os.path.join(a, 'background_2.png')
    if os.path.exists(bg_path):
        bg = pygame.image.load(bg_path).convert()
        iw, ih = bg.get_size()
        nw = int(iw * S.HEIGHT / ih)
        assets['background'] = pygame.transform.scale(bg, (nw, S.HEIGHT))
    else:
        assets['background'] = _make_bg()

    # Menu background
    mb = os.path.join(a, 'blueprint_ship.jpg')
    if os.path.exists(mb):
        assets['menu_bg'] = pygame.image.load(mb).convert()
    else:
        assets['menu_bg'] = _make_bg(color=(10, 20, 50))

    # Story slides
    slides_dir = os.path.join(a, 'StorySlides')
    assets['story_slides'] = [
        pygame.image.load(os.path.join(slides_dir, f'new_{i}.png')).convert()
        for i in range(1, 5)
        if os.path.exists(os.path.join(slides_dir, f'new_{i}.png'))
    ]

    # Rock texture
    rt = os.path.join(a, 'rock_pattern.png')
    assets['rock_texture'] = load_image(rt, (128, 128), (100, 80, 60)) if os.path.exists(rt) else None

    # Projectile images
    assets['bullet']         = load_image(os.path.join(a, 'Guns', 'arduino_bullet.png'),
                                          fallback_size=(28, 10), fallback_color=(255, 220, 80))
    assets['football']       = load_image(os.path.join(a, 'Guns', 'football.png'))
    assets['halfheart_left'] = load_image(os.path.join(a, 'Guns', 'halfheart_left.png'))
    assets['halfheart_right']= load_image(os.path.join(a, 'Guns', 'halfheart_right.png'))

    # Weapon animation frames
    def crop_frames(png_path, rects, target_size):
        sheet  = load_image(png_path)
        frames = []
        for r in rects:
            frame = sheet.subsurface(r).copy()
            frames.append(pygame.transform.scale(frame, target_size))
        return frames

    guns_dir = os.path.join(a, 'Guns')

    assets['anim_pistol'] = crop_frames(
        os.path.join(guns_dir, 'arduinogunatlas.png'),
        [pygame.Rect(2,606,450,300), pygame.Rect(2,304,450,300), pygame.Rect(454,606,450,300),
         pygame.Rect(2,2,450,300),   pygame.Rect(454,304,450,300), pygame.Rect(454,2,450,300)],
        (90, 60),
    )
    assets['anim_football'] = crop_frames(
        os.path.join(guns_dir, 'football_cat.png'),
        [pygame.Rect(2,429,425,425), pygame.Rect(2,2,425,425),
         pygame.Rect(429,429,425,425), pygame.Rect(429,2,425,425)],
        (80, 80),
    )
    assets['anim_hearts'] = crop_frames(
        os.path.join(guns_dir, 'hertbreaker.png'),
        [pygame.Rect(2,404,350,400), pygame.Rect(2,2,350,400),
         pygame.Rect(354,404,350,400), pygame.Rect(354,2,350,400)],
        (65, 75),
    )

    # Hearts (0=empty … 4=full)
    hearts_dir = os.path.join(a, 'Hearts')
    assets['hearts'] = [
        load_image(os.path.join(hearts_dir, f'heart_{i}.png'), (48, 48), (200, 60, 60))
        for i in range(5)
    ]

    # Weapon cards
    cards_dir = os.path.join(a, 'Cards')
    assets['weapon_cards'] = [
        load_image(os.path.join(cards_dir, 'arduino_pistol_card.png'), (80, 100), (60, 80, 160)),
        load_image(os.path.join(cards_dir, 'football_card.png'),       (80, 100), (80, 160, 60)),
        load_image(os.path.join(cards_dir, 'halfheart_card.png'),      (80, 100), (160, 60, 80)),
    ]

    # Sound effects
    sounds = {}
    for name, fname in [('bite', 'bite.wav'), ('click', 'click.wav'), ('teleport', 'teleport.wav')]:
        path = os.path.join(a, fname)
        if os.path.exists(path):
            try:
                sounds[name] = pygame.mixer.Sound(path)
                sounds[name].set_volume(0.5)
            except pygame.error:
                pass
    assets['sounds'] = sounds

    assets['menu_music'] = os.path.join(a, 'game_song.wav')
    assets['game_music'] = os.path.join(a, 'song2.wav')

    return assets


def _make_bg(color=(5, 10, 30)) -> pygame.Surface:
    import random
    surf = pygame.Surface((S.WIDTH, S.HEIGHT))
    surf.fill(color)
    for _ in range(120):
        x, y = random.randrange(S.WIDTH), random.randrange(S.HEIGHT)
        b    = random.randint(140, 255)
        r    = random.randint(1, 2)
        pygame.draw.circle(surf, (b, b, b), (x, y), r)
    return surf


def play_music(path: str, volume=0.4):
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass
    else:
        pygame.mixer.music.stop()


async def main():
    pygame.init()
    pygame.mixer.init()
    surf  = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
    pygame.display.set_caption(S.TITLE)
    clock = pygame.time.Clock()

    assets     = load_assets()
    high_score = load_high_score()

    state: str                      = 'menu'
    screen                          = MenuScreen(assets['menu_bg'], high_score)
    gameplay: GameplayScreen | None = None
    music_on: bool                  = True

    play_music(assets['menu_music'])

    while True:
        dt = clock.tick(S.FPS) / 1000.0
        dt = min(dt, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            result = screen.handle_event(event)

            if result == 'toggle_music':
                music_on = not music_on
                pygame.mixer.music.set_volume(0.4 if music_on else 0.0)

            elif state == 'menu':
                if result == 'story':
                    screen = StoryScreen(assets['story_slides'])
                    state  = 'story'
                elif result == 'play':
                    gameplay = GameplayScreen(assets)
                    screen   = gameplay
                    state    = 'game'
                    play_music(assets['game_music'])
                    pygame.mixer.music.set_volume(0.4 if music_on else 0.0)
                elif result == 'quit':
                    pygame.quit()
                    sys.exit()

            elif state == 'story':
                if result == 'menu':
                    screen = MenuScreen(assets['menu_bg'], high_score)
                    state  = 'menu'

            elif state == 'game':
                if result == 'menu':
                    screen = MenuScreen(assets['menu_bg'], high_score)
                    state  = 'menu'
                    play_music(assets['menu_music'])
                    pygame.mixer.music.set_volume(0.4 if music_on else 0.0)

            elif state == 'gameover':
                if result == 'retry':
                    gameplay = GameplayScreen(assets)
                    screen   = gameplay
                    state    = 'game'
                    play_music(assets['game_music'])
                    pygame.mixer.music.set_volume(0.4 if music_on else 0.0)
                elif result == 'menu':
                    screen = MenuScreen(assets['menu_bg'], high_score)
                    state  = 'menu'
                    play_music(assets['menu_music'])
                    pygame.mixer.music.set_volume(0.4 if music_on else 0.0)

        if state == 'game' and gameplay:
            outcome = gameplay.update(dt)
            if outcome == 'dead':
                final_score = gameplay.score
                if final_score > high_score:
                    high_score = final_score
                    save_high_score(high_score)
                screen = GameOverScreen(final_score, high_score)
                state  = 'gameover'
                play_music(assets['menu_music'], volume=0.3)
        else:
            screen.update(dt)

        surf.fill(S.DARK)
        screen.draw(surf, music_on)
        pygame.display.flip()

        await asyncio.sleep(0)  # yield to browser event loop (required by Pygbag)


asyncio.run(main())
