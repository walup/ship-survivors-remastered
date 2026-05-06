import math
import pygame
import settings as S

FOOTBALL_GRAVITY = 480


class Bullet(pygame.sprite.Sprite):
    damage = 1

    def __init__(self, x, y, image: pygame.Surface, angle_deg: float = 0):
        super().__init__()
        scaled = pygame.transform.scale(image, (32, 16))
        self.image = pygame.Surface((36, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 240, 80, 140), (0, 2, 36, 16))
        self.image.blit(scaled, (2, 2))

        # Rotate bullet image to match travel angle
        if abs(angle_deg) > 2:
            self.image = pygame.transform.rotate(self.image, -angle_deg)

        self.rect = self.image.get_rect(midleft=(x, y))
        self.x, self.y = float(x), float(y)
        rad = math.radians(angle_deg)
        self.vx = math.cos(rad) * S.BULLET_SPEED
        self.vy = math.sin(rad) * S.BULLET_SPEED

    def update(self, dt, *args):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (int(self.x), int(self.y))
        if self.x > S.WIDTH + 30 or self.x < -30 or self.y < -30 or self.y > S.HEIGHT + 30:
            self.kill()


class Football(pygame.sprite.Sprite):
    damage = 2   # one-shots armored rocks

    def __init__(self, x, y, image: pygame.Surface, launch_angle_deg: float = -28):
        super().__init__()
        self.image = pygame.transform.scale(image, (42, 30))
        self.rect  = self.image.get_rect(center=(x, y))
        self.x, self.y = float(x), float(y)

        rad    = math.radians(launch_angle_deg)
        self.vx = math.cos(rad) * S.FOOTBALL_SPEED
        self.vy = math.sin(rad) * S.FOOTBALL_SPEED
        self._rot  = 0.0
        self._base = self.image.copy()

    def update(self, dt, *args):
        self.vy += FOOTBALL_GRAVITY * dt
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.rect.center = (int(self.x), int(self.y))
        self._rot  = (self._rot + 420 * dt) % 360
        self.image = pygame.transform.rotate(self._base, -self._rot)
        self.rect  = self.image.get_rect(center=self.rect.center)
        if self.x > S.WIDTH + 60 or self.x < -60 or self.y > S.HEIGHT + 60:
            self.kill()


class HalfHeart(pygame.sprite.Sprite):
    damage    = 1
    MAX_RANGE = 340   # fades and dies beyond this — short-range weapon

    def __init__(self, x, y, image: pygame.Surface, angle_deg: float):
        super().__init__()
        self.image = pygame.transform.scale(image, (30, 30))
        self._base = self.image.copy()
        self.rect  = self.image.get_rect(center=(x, y))
        self.x, self.y = float(x), float(y)
        rad = math.radians(angle_deg)
        self.vx = math.cos(rad) * S.HALFHEART_SPEED
        self.vy = math.sin(rad) * S.HALFHEART_SPEED
        self._dist = 0.0

    def update(self, dt, *args):
        step = math.hypot(self.vx, self.vy) * dt
        self._dist += step
        if self._dist >= self.MAX_RANGE:
            self.kill()
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (int(self.x), int(self.y))

        # Fade out as it approaches max range
        alpha = int(255 * (1 - self._dist / self.MAX_RANGE))
        self.image = self._base.copy()
        self.image.set_alpha(alpha)

        if self.x > S.WIDTH + 40 or self.x < -40 or self.y < -40 or self.y > S.HEIGHT + 40:
            self.kill()
