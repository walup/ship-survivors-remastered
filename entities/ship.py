import pygame
import settings as S


class Ship(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface):
        super().__init__()
        self.image = pygame.transform.scale(image, (156, 92))
        self.rect  = self.image.get_rect(midleft=(S.SHIP_X - 10, S.HEIGHT // 2))
        self.y     = float(self.rect.centery)
        self.vel_y = 0.0

        self.health = S.MAX_HEARTS * S.HEART_PIECES  # 12
        self.immunity_timer = 0.0
        self.flash_timer    = 0.0
        self._base_image    = self.image.copy()

    # ------------------------------------------------------------------ #
    def update(self, dt: float, keys):
        dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy =  1

        self.y += dy * S.SHIP_SPEED * dt
        self.y  = max(self.rect.height // 2,
                      min(S.HEIGHT - self.rect.height // 2, self.y))
        self.rect.centery = int(self.y)

        if self.immunity_timer > 0:
            self.immunity_timer -= dt
        if self.flash_timer > 0:
            self.flash_timer -= dt

    # ------------------------------------------------------------------ #
    def take_hit(self) -> bool:
        if self.immunity_timer > 0:
            return False
        self.health -= 1
        self.immunity_timer = S.HIT_IMMUNITY
        self.flash_timer    = S.HIT_IMMUNITY
        return True

    @property
    def dead(self):
        return self.health <= 0

    @property
    def is_flashing(self):
        return self.flash_timer > 0 and int(self.flash_timer * 8) % 2 == 0

    # ------------------------------------------------------------------ #
    def draw(self, surf: pygame.Surface):
        if self.is_flashing:
            tinted = self._base_image.copy()
            tinted.fill((255, 80, 80, 120), special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(tinted, self.rect)
        else:
            surf.blit(self.image, self.rect)
