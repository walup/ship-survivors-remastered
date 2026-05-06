import pygame
import settings as S
from screens.gameplay import _draw_music_btn


class MenuScreen:
    def __init__(self, bg: pygame.Surface, high_score: int):
        iw, ih   = bg.get_size()
        scale    = max(S.WIDTH / iw, S.HEIGHT / ih)
        nw, nh   = int(iw * scale), int(ih * scale)
        scaled   = pygame.transform.scale(bg, (nw, nh))
        cx, cy   = (nw - S.WIDTH) // 2, (nh - S.HEIGHT) // 2
        self.bg  = scaled.subsurface(pygame.Rect(cx, cy, S.WIDTH, S.HEIGHT)).copy()
        self.high_score = high_score
        self.font_title = pygame.font.SysFont('Arial', 52, bold=True)
        self.font_big   = pygame.font.SysFont('Arial', 28, bold=True)
        self.font_med   = pygame.font.SysFont('Arial', 20)
        self.btn_play   = pygame.Rect(S.WIDTH // 2 - 115, 215, 230, 46)
        self.btn_story  = pygame.Rect(S.WIDTH // 2 - 115, 281, 230, 46)
        self.btn_quit   = pygame.Rect(S.WIDTH // 2 - 115, 347, 230, 46)
        self.btn_music  = pygame.Rect(S.WIDTH - 54, 10, 40, 40)
        self._t = 0.0

    def handle_event(self, event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_play.collidepoint(event.pos):
                return 'play'
            if self.btn_story.collidepoint(event.pos):
                return 'story'
            if self.btn_quit.collidepoint(event.pos):
                return 'quit'
            if self.btn_music.collidepoint(event.pos):
                return 'toggle_music'
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return 'play'
            if event.key == pygame.K_ESCAPE:
                return 'quit'
            if event.key == pygame.K_m:
                return 'toggle_music'
        return None

    def update(self, dt: float):
        self._t += dt

    def draw(self, surf: pygame.Surface, music_on: bool = True):
        surf.blit(self.bg, (0, 0))

        # Semi-transparent overlay
        overlay = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 15, 160))
        surf.blit(overlay, (0, 0))

        # Animated title glow
        import math
        glow_a = int(140 + 80 * math.sin(self._t * 2))
        title_shadow = self.font_title.render('Ship Survivors', True, (0, 0, 0))
        title_main   = self.font_title.render('Ship Survivors', True, S.WHITE)
        title_accent = self.font_title.render('Ship Survivors', True,
                                               (80, 200 + int(55 * math.sin(self._t)), 255))

        tx = S.WIDTH // 2 - title_main.get_width() // 2
        surf.blit(title_shadow, (tx + 3, 91))
        surf.blit(title_accent, (tx, 88))
        surf.blit(title_main,   (tx, 88))

        # High score
        if self.high_score > 0:
            hs = self.font_med.render(f'Best: {self.high_score:,}', True, S.YELLOW)
            surf.blit(hs, (S.WIDTH // 2 - hs.get_width() // 2, 155))

        subtitle = self.font_med.render('Survive the rocks!', True, S.GRAY)
        surf.blit(subtitle, (S.WIDTH // 2 - subtitle.get_width() // 2, 180))

        # Buttons
        mouse = pygame.mouse.get_pos()
        for rect, label, color in [
            (self.btn_play,  'PLAY',  (55, 160, 255)),
            (self.btn_story, 'STORY', (80, 130, 180)),
            (self.btn_quit,  'QUIT',  (180, 55,  55)),
        ]:
            hover = rect.collidepoint(mouse)
            bg_c  = tuple(min(255, c + 40) for c in color) if hover else color
            pygame.draw.rect(surf, bg_c, rect, border_radius=10)
            pygame.draw.rect(surf, S.WHITE, rect, 2, border_radius=10)
            lbl = self.font_big.render(label, True, S.WHITE)
            surf.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                            rect.centery - lbl.get_height() // 2))

        # Music toggle button (top-right)
        _draw_music_btn(surf, self.btn_music, music_on)

        # Controls hint
        hint = self.font_med.render('W/S or ↑↓ Move  ·  1/2/3 Select weapon  ·  Space / Click Fire  ·  M Music', True, S.GRAY)
        surf.blit(hint, (S.WIDTH // 2 - hint.get_width() // 2, S.HEIGHT - 22))
