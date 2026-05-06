import pygame
import settings as S


class GameOverScreen:
    def __init__(self, score: int, high_score: int):
        self.score      = score
        self.high_score = high_score
        self.new_best   = score > high_score
        self.font_big   = pygame.font.SysFont('Arial', 52, bold=True)
        self.font_med   = pygame.font.SysFont('Arial', 28, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 20)
        self.btn_menu   = pygame.Rect(S.WIDTH // 2 - 120, 340, 240, 54)
        self.btn_retry  = pygame.Rect(S.WIDTH // 2 - 120, 270, 240, 54)
        self._t = 0.0

    def handle_event(self, event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_retry.collidepoint(event.pos):
                return 'retry'
            if self.btn_menu.collidepoint(event.pos):
                return 'menu'
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                return 'retry'
            if event.key == pygame.K_ESCAPE:
                return 'menu'
        return None

    def update(self, dt):
        self._t += dt

    def draw(self, surf: pygame.Surface, music_on: bool = True):
        overlay = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 20, 230))
        surf.blit(overlay, (0, 0))

        # Game Over title
        go = self.font_big.render('GAME OVER', True, S.RED)
        surf.blit(go, (S.WIDTH // 2 - go.get_width() // 2, 80))

        # Score
        sc = self.font_med.render(f'Score: {self.score:,}', True, S.WHITE)
        surf.blit(sc, (S.WIDTH // 2 - sc.get_width() // 2, 155))

        if self.new_best:
            import math
            pulse = int(200 + 55 * math.sin(self._t * 4))
            nb = self.font_med.render('NEW BEST!', True, (255, pulse, 0))
            surf.blit(nb, (S.WIDTH // 2 - nb.get_width() // 2, 195))
        else:
            hs = self.font_small.render(f'Best: {self.high_score:,}', True, S.GRAY)
            surf.blit(hs, (S.WIDTH // 2 - hs.get_width() // 2, 200))

        mouse = pygame.mouse.get_pos()
        for rect, label, color in [
            (self.btn_retry, 'RETRY',     (55, 160, 255)),
            (self.btn_menu,  'MAIN MENU', (100, 100, 130)),
        ]:
            hover = rect.collidepoint(mouse)
            bg_c  = tuple(min(255, c + 40) for c in color) if hover else color
            pygame.draw.rect(surf, bg_c, rect, border_radius=10)
            pygame.draw.rect(surf, S.WHITE, rect, 2, border_radius=10)
            lbl = self.font_med.render(label, True, S.WHITE)
            surf.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                            rect.centery - lbl.get_height() // 2))

        hint = self.font_small.render('R  Retry   ·   Esc  Menu', True, S.GRAY)
        surf.blit(hint, (S.WIDTH // 2 - hint.get_width() // 2, S.HEIGHT - 30))
