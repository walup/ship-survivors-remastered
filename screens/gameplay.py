import random, math
import pygame
import settings as S


def _draw_music_btn(surf: pygame.Surface, rect: pygame.Rect, music_on: bool):
    bg = (60, 60, 80) if music_on else (80, 40, 40)
    pygame.draw.rect(surf, bg, rect, border_radius=6)
    pygame.draw.rect(surf, S.WHITE, rect, 2, border_radius=6)
    cx, cy = rect.centerx, rect.centery
    # Speaker body
    body = pygame.Rect(cx - 10, cy - 6, 8, 12)
    pygame.draw.rect(surf, S.WHITE, body)
    cone = [(cx - 2, cy - 6), (cx + 6, cy - 11), (cx + 6, cy + 11), (cx - 2, cy + 6)]
    pygame.draw.polygon(surf, S.WHITE, cone)
    if music_on:
        # Sound wave arcs
        for r, a in [(8, 35), (13, 45)]:
            pygame.draw.arc(surf, S.WHITE,
                            pygame.Rect(cx + 3, cy - r, r, r * 2),
                            math.radians(-a), math.radians(a), 2)
    else:
        # Mute X
        pygame.draw.line(surf, (220, 80, 80), (cx + 5, cy - 8), (cx + 14, cy + 8), 3)
        pygame.draw.line(surf, (220, 80, 80), (cx + 14, cy - 8), (cx + 5, cy + 8), 3)
from entities.ship       import Ship
from entities.rock       import Rock
from entities.projectile import Bullet, Football, HalfHeart
from particles           import ParticleSystem
from ui.hud              import HUD


# ------------------------------------------------------------------ #
class WeaponAnimator:
    def __init__(self, frames: list[pygame.Surface], fps: float = 10):
        self.frames = frames
        self._spf   = 1.0 / fps
        self._t     = 0.0
        self._idx   = 0

    def update(self, dt: float):
        self._t += dt
        while self._t >= self._spf:
            self._t  -= self._spf
            self._idx = (self._idx + 1) % len(self.frames)

    @property
    def image(self) -> pygame.Surface:
        return self.frames[self._idx]


# ------------------------------------------------------------------ #
# Wave definitions — each entry: (fast_chance, armored_chance, speed_mult, max_rocks, spawn_interval)
_WAVES = [
    #  fast   armored  spd   max  interval
    (0.00,  0.00,   1.00,  4,   3.8),   # wave 1
    (0.20,  0.00,   1.15,  5,   3.2),   # wave 2
    (0.25,  0.15,   1.30,  6,   2.6),   # wave 3
    (0.30,  0.25,   1.50,  7,   2.1),   # wave 4
    (0.35,  0.30,   1.70,  8,   1.7),   # wave 5+
]

_WEAPON_ANIM_FPS = [14, 10, 10]
_WEAPON_KEYS     = ['anim_pistol', 'anim_football', 'anim_hearts']


class GameplayScreen:
    def __init__(self, assets: dict):
        self._assets = assets
        self.reset()

    # ------------------------------------------------------------------ #
    def reset(self):
        a = self._assets
        self.ship        = Ship(a['ship'])
        self.rocks       = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.particles   = ParticleSystem()
        self.hud         = HUD(a['hearts'], a['weapon_cards'], ['Pistol', 'Football', 'Hearts'])

        self.score         = 0
        self.active_weapon = 0
        self._spawn_timer  = 0.0
        self._bg_scroll    = 0.0
        self._shake        = 0.0
        self._paused       = False

        # Wave system
        self._wave         = 1
        self._wave_timer   = 0.0
        self._banner_timer = 0.0   # > 0 while banner is visible
        self._banner_text  = ''

        self._bg       = a['background']
        self._rock_tex = a.get('rock_texture')
        self._bullet   = a['bullet']
        self._football = a['football']
        self._hl       = a['halfheart_left']
        self._hr       = a['halfheart_right']
        self._sounds   = a.get('sounds', {})

        self._animators = [
            WeaponAnimator(a[key], fps=_WEAPON_ANIM_FPS[i])
            for i, key in enumerate(_WEAPON_KEYS)
        ]

        self._font_banner = pygame.font.SysFont('Arial', 52, bold=True)
        self._pause_btn   = pygame.Rect(S.WIDTH - 50,  8, 40, 40)
        self._music_btn   = pygame.Rect(S.WIDTH - 96,  8, 40, 40)
        self._resume_btn  = pygame.Rect(S.WIDTH // 2 - 100, 190, 200, 48)
        self._menu_btn    = pygame.Rect(S.WIDTH // 2 - 100, 256, 200, 48)

    # ------------------------------------------------------------------ #
    def _wave_cfg(self):
        idx = min(self._wave - 1, len(_WAVES) - 1)
        return _WAVES[idx]

    # ------------------------------------------------------------------ #
    def handle_event(self, event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._paused = not self._paused
            if event.key == pygame.K_1: self._switch_weapon(0)
            if event.key == pygame.K_2: self._switch_weapon(1)
            if event.key == pygame.K_3: self._switch_weapon(2)
            if not self._paused and event.key == pygame.K_SPACE:
                self._fire()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._paused:
                if self._resume_btn.collidepoint(event.pos):
                    self._paused = False
                if self._menu_btn.collidepoint(event.pos):
                    return 'menu'
            else:
                if self._pause_btn.collidepoint(event.pos):
                    self._paused = True
                    return None
                if self._music_btn.collidepoint(event.pos):
                    return 'toggle_music'
                card_w = 80
                panel_w = 3 * card_w + 2 * 8 + 20
                px = (S.WIDTH - panel_w) // 2
                py = S.HEIGHT - 120
                for i in range(3):
                    if pygame.Rect(px + i * (card_w + 8), py, card_w, 100).collidepoint(event.pos):
                        self._switch_weapon(i)
                        return None
                self._fire()
        return None

    def _switch_weapon(self, idx: int):
        self.active_weapon = idx

    # ------------------------------------------------------------------ #
    def _weapon_draw_pos(self) -> tuple[int, int]:
        anim = self._animators[self.active_weapon]
        img  = anim.image
        wx = self.ship.rect.centerx - img.get_width() // 2
        wy = self.ship.rect.top - img.get_height() + 14
        return wx, wy

    def _fire(self):
        wx, wy   = self._weapon_draw_pos()
        anim     = self._animators[self.active_weapon]
        launch_x = wx + anim.image.get_width()
        launch_y = wy + anim.image.get_height() // 2
        mx, my   = pygame.mouse.get_pos()

        if self.active_weapon == 0:
            self.projectiles.add(Bullet(launch_x, launch_y, self._bullet, 0))
            self._play('click')

        elif self.active_weapon == 1:
            angle = -28 + random.uniform(-6, 6)
            self.projectiles.add(Football(launch_x, launch_y, self._football, angle))
            self._play('teleport')

        elif self.active_weapon == 2:
            # Three half-hearts: straight right + angled up/down
            for angle, img in [(-25, self._hl), (0, self._hl), (25, self._hr)]:
                self.projectiles.add(HalfHeart(launch_x, launch_y, img, angle))
            self._play('teleport')

    def _play(self, name):
        snd = self._sounds.get(name)
        if snd:
            snd.play()

    # ------------------------------------------------------------------ #
    def _pick_rock_type(self) -> str:
        fast_c, arm_c, *_ = self._wave_cfg()
        r = random.random()
        if r < arm_c:
            return 'armored'
        if r < arm_c + fast_c:
            return 'fast'
        return 'normal'

    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> str | None:
        if self._paused:
            return None

        keys = pygame.key.get_pressed()
        self.ship.update(dt, keys)
        self._animators[self.active_weapon].update(dt)
        self.hud.update(dt, keys, self.active_weapon)

        # --- Wave progression ---
        self._wave_timer += dt
        if self._wave_timer >= S.WAVE_DURATION:
            self._wave_timer -= S.WAVE_DURATION
            self._wave       += 1
            self._banner_timer = 2.5
            self._banner_text  = f'WAVE  {self._wave}'
            # Speed up existing rocks
            _, _, spd_mult, _, _ = self._wave_cfg()
            prev_spd_mult = _WAVES[min(self._wave - 3, len(_WAVES) - 1)][2] if self._wave > 2 else 1.0
            ratio = spd_mult / max(prev_spd_mult, 0.01)
            for rock in self.rocks:
                rock.speed *= ratio

        if self._banner_timer > 0:
            self._banner_timer -= dt

        # --- Spawn rocks ---
        _, _, spd_mult, max_rocks, interval = self._wave_cfg()
        self._spawn_timer -= dt
        if self._spawn_timer <= 0 and len(self.rocks) < max_rocks:
            sizes = ['large', 'medium', 'small']
            # Bias toward larger rocks at higher waves
            weights = [0.4 + 0.1 * (self._wave - 1),
                       0.4,
                       max(0.1, 0.2 - 0.05 * (self._wave - 1))]
            total = sum(weights)
            weights = [w / total for w in weights]
            r = random.random()
            cum = 0
            size = 'medium'
            for s, w in zip(sizes, weights):
                cum += w
                if r < cum:
                    size = s
                    break
            rtype = self._pick_rock_type()
            ry = random.randint(S.ROCK_RADII[size] + 10, S.HEIGHT - S.ROCK_RADII[size] - 10)
            rock = Rock(size, S.WIDTH + S.ROCK_RADII[size], ry, self._rock_tex, rtype)
            rock.speed *= spd_mult
            self.rocks.add(rock)
            self._spawn_timer = interval * random.uniform(0.8, 1.2)

        # --- Update groups ---
        self.projectiles.update(dt)
        self.rocks.update(dt)
        for rock in self.rocks:
            if rock.seeker:
                rock.steer_toward(self.ship.rect.centery, dt)
        self.particles.update(dt)

        # --- Remove off-screen rocks ---
        for rock in list(self.rocks):
            if rock.off_screen():
                rock.kill()

        # --- Projectile vs rock ---
        for proj in list(self.projectiles):
            if not proj.alive():
                continue
            for rock in list(self.rocks):
                pr = proj.rect
                rc = rock.rect
                dx = max(rc.left, min(pr.centerx, rc.right))  - pr.centerx
                dy = max(rc.top,  min(pr.centery, rc.bottom)) - pr.centery
                if dx * dx + dy * dy < rock.radius ** 2:
                    cx, cy = rock.rect.center
                    destroyed = rock.hit(getattr(proj, 'damage', 1))
                    if destroyed:
                        for child in rock.split():
                            child.speed *= _WAVES[min(self._wave - 1, len(_WAVES) - 1)][2]
                            self.rocks.add(child)
                        self.score += rock.score
                        rock.kill()
                        boom_color = {
                            'fast':    (240, 120, 40),
                            'armored': (100, 160, 240),
                            'normal':  (200, 140, 80),
                        }[rock.rock_type]
                        self.particles.explosion(cx, cy, color=boom_color, count=22)
                    else:
                        self.particles.sparks(cx, cy)
                    self._play('bite')
                    proj.kill()
                    break

        # --- Rock vs ship ---
        for rock in list(self.rocks):
            if rock.rect.colliderect(self.ship.rect):
                if self.ship.take_hit():
                    self._shake = 0.38
                    self.particles.explosion(self.ship.rect.centerx, self.ship.rect.centery,
                                             color=S.RED, count=14, speed=180)
                    self._play('bite')

        if self._shake > 0:
            self._shake = max(0.0, self._shake - dt * 1.5)


        bw = self._bg.get_width()
        self._bg_scroll = (self._bg_scroll + 60 * dt) % bw

        if self.ship.dead:
            return 'dead'
        return None

    # ------------------------------------------------------------------ #
    def draw(self, surf: pygame.Surface, music_on: bool = True):
        ox = oy = 0
        if self._shake > 0:
            mag = int(self._shake * 18)
            ox  = random.randint(-mag, mag)
            oy  = random.randint(-mag, mag)

        bw = self._bg.get_width()
        for bx in range(-int(self._bg_scroll), S.WIDTH, bw):
            surf.blit(self._bg, (bx + ox, oy))

        for rock in self.rocks:
            rock.draw(surf, (ox, oy))

        for proj in self.projectiles:
            surf.blit(proj.image, (proj.rect.x + ox, proj.rect.y + oy))

        self.particles.draw(surf, (ox, oy))
        self.ship.draw(surf)

        wx, wy = self._weapon_draw_pos()
        surf.blit(self._animators[self.active_weapon].image, (wx, wy))

        self.hud.draw(surf, self.ship.health, self.score, self.active_weapon, self._wave)

        # Wave banner
        if self._banner_timer > 0:
            alpha = min(255, int(self._banner_timer * 180))
            txt   = self._font_banner.render(self._banner_text, True, (80, 200, 255))
            txt.set_alpha(alpha)
            surf.blit(txt, (S.WIDTH // 2 - txt.get_width() // 2, S.HEIGHT // 2 - 40))

        # Music button
        _draw_music_btn(surf, self._music_btn, music_on)

        # Pause button
        pygame.draw.rect(surf, (60, 60, 80), self._pause_btn, border_radius=6)
        pygame.draw.rect(surf, S.WHITE, self._pause_btn, 2, border_radius=6)
        for bx in (self._pause_btn.x + 10, self._pause_btn.x + 22):
            pygame.draw.rect(surf, S.WHITE, (bx, self._pause_btn.y + 10, 6, 20))

        if self._paused:
            self._draw_pause(surf)

    def _draw_pause(self, surf):
        dim = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 15, 190))
        surf.blit(dim, (0, 0))
        font = pygame.font.SysFont('Arial', 42, bold=True)
        lbl  = font.render('PAUSED', True, S.WHITE)
        surf.blit(lbl, (S.WIDTH // 2 - lbl.get_width() // 2, 130))
        mouse = pygame.mouse.get_pos()
        for rect, label, color in [
            (self._resume_btn, 'RESUME',    (55, 160, 255)),
            (self._menu_btn,   'MAIN MENU', (100, 100, 130)),
        ]:
            hover = rect.collidepoint(mouse)
            bg_c  = tuple(min(255, c + 40) for c in color) if hover else color
            pygame.draw.rect(surf, bg_c, rect, border_radius=10)
            pygame.draw.rect(surf, S.WHITE, rect, 2, border_radius=10)
            fnt = pygame.font.SysFont('Arial', 26, bold=True)
            txt = fnt.render(label, True, S.WHITE)
            surf.blit(txt, (rect.centerx - txt.get_width() // 2,
                            rect.centery - txt.get_height() // 2))
