import random, math
import pygame
import settings as S


_BASE_COLORS = {
    'large':  (140, 100,  70),
    'medium': (110,  80,  55),
    'small':  ( 90,  65,  45),
}
_CHILDREN = {'large': 'medium', 'medium': 'small', 'small': None}
_SCORE    = {'large': S.SCORE_LARGE, 'medium': S.SCORE_MEDIUM, 'small': S.SCORE_SMALL}

_TYPE_TINT  = {'normal': None, 'fast': (230, 90, 30), 'armored': (60, 100, 160)}
_TYPE_SPEED = {'normal': 1.0,  'fast': 1.85,          'armored': 0.80}
_TYPE_HP    = {'normal': 1,    'fast': 1,              'armored': 2}
_TYPE_SCORE = {'normal': 1.0,  'fast': 1.5,            'armored': 2.5}

_SPLIT_SPEED_BOOST = 1.38
_SEEKER_PULL       = 110


def _blend(base, tint, t=0.55):
    return tuple(int(b * (1 - t) + c * t) for b, c in zip(base, tint))


class Rock(pygame.sprite.Sprite):
    def __init__(self, size: str, x: float, y: float,
                 texture: pygame.Surface | None = None,
                 rock_type: str = 'normal',
                 seeker: bool = False):
        super().__init__()
        self.size_name  = size
        self.rock_type  = rock_type
        self.seeker     = seeker and (size == 'small')
        self.radius     = S.ROCK_RADII[size]
        self.speed      = S.ROCK_SPEEDS[size] * _TYPE_SPEED[rock_type]
        self.score      = int(_SCORE[size] * _TYPE_SCORE[rock_type])
        self.max_hp     = _TYPE_HP[rock_type]
        self.hp         = self.max_hp
        self.vy         = 0.0
        self._dmg_flash = 0.0   # white flash timer after taking a hit

        if self.seeker:
            self.speed *= 1.25

        base = _BASE_COLORS[size]
        tint = _TYPE_TINT[rock_type]
        self.color = _blend(base, tint) if tint else base

        d = self.radius * 2
        self.image   = pygame.Surface((d, d), pygame.SRCALPHA)
        self._verts  = self._make_verts(random.randint(7, 11))
        self._texture = texture
        self._build_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.x, self.y = float(x), float(y)

    # ------------------------------------------------------------------ #
    def _make_verts(self, n):
        r = self.radius
        return [(r + r * random.uniform(0.70, 1.0) * math.cos(i / n * math.tau),
                 r + r * random.uniform(0.70, 1.0) * math.sin(i / n * math.tau))
                for i in range(n)]

    def _build_image(self, cracked: bool = False):
        self.image.fill((0, 0, 0, 0))
        r = self.radius

        # When damaged, shift color toward red/orange
        color = self.color
        if cracked and self.rock_type == 'armored':
            color = _blend(self.color, (200, 60, 30), 0.45)

        pygame.draw.polygon(self.image, color, self._verts)

        if self.rock_type == 'armored':
            lighter = tuple(min(255, c + 60) for c in color)
            pygame.draw.polygon(self.image, lighter, self._verts, 3)

        darker = tuple(max(0, c - 45) for c in color)
        pygame.draw.polygon(self.image, darker, self._verts, 2)

        if self._texture:
            tex = pygame.transform.scale(self._texture, (r * 2, r * 2))
            tex.set_alpha(55)
            self.image.blit(tex, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        if self.rock_type == 'fast':
            for _ in range(3):
                lx = random.randint(r // 2, r * 2 - r // 4)
                ly = random.randint(r // 3, r * 2 - r // 3)
                pygame.draw.line(self.image, (255, 200, 80, 180), (lx - 6, ly), (lx + 6, ly), 1)

        # Bright white crack lines — very visible
        if cracked:
            cx = cy = r
            for _ in range(5):
                angle  = random.uniform(0, math.tau)
                length = random.randint(r // 2, r)
                ex = int(cx + math.cos(angle) * length)
                ey = int(cy + math.sin(angle) * length)
                pygame.draw.line(self.image, (255, 255, 220), (cx, cy), (ex, ey), 2)
                # Thin dark border on crack for contrast
                pygame.draw.line(self.image, (30, 20, 10), (cx, cy), (ex, ey), 1)

        # Seeker "eye"
        if self.seeker:
            cr = max(3, r // 3)
            pygame.draw.circle(self.image, (255, 80,  0),   (r, r), cr)
            pygame.draw.circle(self.image, (255, 200, 80),  (r, r), max(1, cr - 2))

    # ------------------------------------------------------------------ #
    def hit(self, damage: int = 1) -> bool:
        self.hp -= damage
        if self.hp <= 0:
            return True
        # Survived — rebuild with cracks and trigger flash
        self._build_image(cracked=True)
        self._dmg_flash = 0.20
        return False

    def update(self, dt, *args):
        self.x -= self.speed * dt
        self.y += self.vy * dt
        self.rect.center = (int(self.x), int(self.y))
        if self._dmg_flash > 0:
            self._dmg_flash -= dt

    def steer_toward(self, ship_y: float, dt: float):
        dy = ship_y - self.y
        self.vy += dy * 0.8 * dt * (_SEEKER_PULL / max(abs(dy), 1))
        max_vy = self.speed * 0.65
        self.vy = max(-max_vy, min(max_vy, self.vy))
        if self.y - self.radius < 0:
            self.y, self.vy = self.radius, abs(self.vy)
        elif self.y + self.radius > S.HEIGHT:
            self.y, self.vy = S.HEIGHT - self.radius, -abs(self.vy)

    def off_screen(self):
        return self.x + self.radius < 0

    def split(self) -> list['Rock']:
        child_size = _CHILDREN[self.size_name]
        if child_size is None:
            return []
        cx, cy    = self.rect.center
        child_type = self.rock_type if self.rock_type == 'fast' else 'normal'
        children  = []
        for sign in (-1, 1):
            is_seeker = (self.rock_type == 'fast') or (random.random() < 0.35)
            child = Rock(child_size, cx, cy + sign * self.radius * 0.5,
                         rock_type=child_type, seeker=is_seeker)
            child.speed *= _SPLIT_SPEED_BOOST
            children.append(child)
        return children

    def draw(self, surf: pygame.Surface, offset=(0, 0)):
        dx, dy = offset
        dest   = (self.rect.x + dx, self.rect.y + dy)

        # White damage flash overlay
        if self._dmg_flash > 0:
            flash = self.image.copy()
            alpha = int(200 * (self._dmg_flash / 0.20))
            flash.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(flash, dest)
        else:
            surf.blit(self.image, dest)

        # HP dots for armored rocks (small squares above the rock)
        if self.rock_type == 'armored' and self.max_hp > 1:
            dot_size = 5
            spacing  = 8
            total_w  = self.max_hp * dot_size + (self.max_hp - 1) * (spacing - dot_size)
            ox       = self.rect.centerx + dx - total_w // 2
            oy       = self.rect.top + dy - 8
            for i in range(self.max_hp):
                color = (80, 200, 255) if i < self.hp else (60, 60, 80)
                pygame.draw.rect(surf, color,
                                 (ox + i * spacing, oy, dot_size, dot_size),
                                 border_radius=1)
