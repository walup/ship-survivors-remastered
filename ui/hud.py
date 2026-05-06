import pygame
import settings as S

_CARD_W   = 80
_CARD_H   = 100
_CARD_GAP = 12
_PEEK_IDLE   = 18   # px of card visible when not the active weapon
_PEEK_ACTIVE = 30   # px visible when it's the active weapon but key not held
_FULL_RISE   = _CARD_H + 16   # px above bottom edge when fully drawn


class HUD:
    def __init__(self, heart_images: list[pygame.Surface],
                 weapon_cards: list[pygame.Surface],
                 weapon_names: list[str]):
        self.heart_imgs  = [pygame.transform.scale(img, (48, 46)) for img in heart_images]
        self.card_imgs   = [pygame.transform.scale(img, (_CARD_W, _CARD_H)) for img in weapon_cards]
        self.names       = weapon_names
        self.font_big    = pygame.font.SysFont('Arial', 26, bold=True)
        self.font_small  = pygame.font.SysFont('Arial', 14, bold=True)
        self.font_wave   = pygame.font.SysFont('Arial', 18, bold=True)

        # How far each card has risen above its tucked position (0=tucked, 1=fully drawn)
        self._rise = [0.0] * len(weapon_cards)

        # Pre-build card x positions (centred on screen)
        n = len(weapon_cards)
        total_w = n * _CARD_W + (n - 1) * _CARD_GAP
        self._card_xs = [S.WIDTH // 2 - total_w // 2 + i * (_CARD_W + _CARD_GAP)
                         for i in range(n)]

        # Holster bracket surface (drawn once)
        self._holster = self._make_holster(total_w)
        self._holster_x = S.WIDTH // 2 - total_w // 2 - 8

    def _make_holster(self, total_w: int) -> pygame.Surface:
        h = 14
        surf = pygame.Surface((total_w + 16, h), pygame.SRCALPHA)
        surf.fill((30, 35, 50, 210))
        pygame.draw.rect(surf, (80, 200, 255, 160), surf.get_rect(), 2, border_radius=4)
        # Slot dividers
        n = len(self.card_imgs)
        for i in range(1, n):
            x = 8 + i * (_CARD_W + _CARD_GAP) - _CARD_GAP // 2
            pygame.draw.line(surf, (80, 200, 255, 100), (x, 0), (x, h))
        return surf

    # ------------------------------------------------------------------ #
    def update(self, dt: float, keys, active: int):
        for i in range(len(self._rise)):
            key_held = keys[pygame.K_1 + i]
            if key_held:
                target = 1.0
            elif i == active:
                target = _PEEK_ACTIVE / _FULL_RISE
            else:
                target = _PEEK_IDLE / _FULL_RISE

            speed = 14.0 if target > self._rise[i] else 8.0
            self._rise[i] += (target - self._rise[i]) * speed * dt
            self._rise[i]  = max(0.0, min(1.0, self._rise[i]))

    # ------------------------------------------------------------------ #
    def draw(self, surf: pygame.Surface, health: int, score: int,
             active_weapon: int, wave: int = 1):
        self._draw_hearts(surf, health)
        self._draw_score(surf, score, wave)
        self._draw_holster(surf, active_weapon)

    # ------------------------------------------------------------------ #
    def _draw_hearts(self, surf, health):
        x = 12
        for i in range(S.MAX_HEARTS):
            remaining = health - i * S.HEART_PIECES
            idx = max(0, min(S.HEART_PIECES, remaining))
            surf.blit(self.heart_imgs[idx], (x, 10))
            x += 54

    def _draw_score(self, surf, score, wave):
        label  = self.font_big.render(f'{score:,}', True, S.WHITE)
        shadow = self.font_big.render(f'{score:,}', True, (0, 0, 0))
        sy = S.HEIGHT - 36
        sx = S.WIDTH - label.get_width() - 14
        surf.blit(shadow, (sx + 1, sy + 1))
        surf.blit(label,  (sx,     sy))

        wave_color = (80, 200, 255) if wave < 4 else (255, 160, 40)
        wlbl = self.font_wave.render(f'WAVE {wave}', True, wave_color)
        wsh  = self.font_wave.render(f'WAVE {wave}', True, (0, 0, 0))
        wy = sy - wlbl.get_height() - 4
        wx = S.WIDTH - wlbl.get_width() - 14
        surf.blit(wsh,  (wx + 1, wy + 1))
        surf.blit(wlbl, (wx,     wy))

    def _draw_holster(self, surf, active):
        # Holster bracket sits flush at the very bottom
        surf.blit(self._holster, (self._holster_x, S.HEIGHT - self._holster.get_height()))

        for i, card in enumerate(self.card_imgs):
            rise_px = self._rise[i] * _FULL_RISE          # px card has risen above screen bottom
            card_top = S.HEIGHT - int(rise_px)             # top-left Y of card
            cx = self._card_xs[i]

            # Card shadow when drawn out enough to matter
            if rise_px > _PEEK_IDLE + 10:
                shadow = pygame.Surface((_CARD_W + 6, _CARD_H + 6), pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 80))
                surf.blit(shadow, (cx - 3, card_top - 3))

            # Clip card to screen — only draw the portion that's risen above the bottom edge
            visible_h = min(_CARD_H, int(rise_px))
            if visible_h <= 0:
                continue
            src_rect = pygame.Rect(0, _CARD_H - visible_h, _CARD_W, visible_h)
            surf.blit(card, (cx, card_top), src_rect)

            # Active highlight border
            if i == active:
                border_color = S.ACCENT
                border_top   = max(card_top, S.HEIGHT - int(rise_px))
                border_h     = min(_CARD_H, int(rise_px))
                pygame.draw.rect(surf, border_color,
                                 (cx - 2, border_top - 2, _CARD_W + 4, border_h + 4), 2, border_radius=4)

            # Key label — always visible, sits in the holster strip
            lbl_color = S.ACCENT if i == active else (160, 170, 190)
            lbl = self.font_small.render(str(i + 1), True, lbl_color)
            lx  = cx + _CARD_W // 2 - lbl.get_width() // 2
            ly  = S.HEIGHT - self._holster.get_height() + 1
            surf.blit(lbl, (lx, ly))
