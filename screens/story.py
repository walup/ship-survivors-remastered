import pygame
import settings as S

_LYRICS = [
    [
        "Moon cat has turned earth into a mechanical, predictable world.",
        "In this wasteland, there's no higher ground to stand than bottom of the pile.",
    ],
    [
        "When you can't really function you're so full of fear.",
        "This is the end of the road, this is the end of the line.",
        "That's just the way it is.  Things will never be the same.",
    ],
    [
        "An orphan swims everyday in the same polluted mess.",
        "In an old machine her parents preserved for fifty odd years.",
        "One fine day, in a long forgotten cave,",
        "she finds the carrier of the green flame.",
    ],
    [
        "It confers the ship its powers.",
        "“This day we fight.”",
        "She rides majestic, past homes of men",
        "who care not, or gaze with joy…",
    ],
]


class StoryScreen:
    def __init__(self, slides: list[pygame.Surface]):
        self._slides   = slides
        self._idx      = 0
        self._font     = pygame.font.SysFont('Georgia', 17, italic=True)
        self._font_nav = pygame.font.SysFont('Arial', 14)
        self._fade     = 0.0          # 0=black, 1=fully visible
        self._fading_in = True

    # ------------------------------------------------------------------ #
    def handle_event(self, event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'menu'
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT):
                return self._advance()
            if event.key == pygame.K_LEFT and self._idx > 0:
                self._idx -= 1
                self._fade = 0.0
                self._fading_in = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._advance()
        return None

    def _advance(self) -> str | None:
        if self._idx < len(self._slides) - 1:
            self._idx += 1
            self._fade = 0.0
            self._fading_in = True
            return None
        return 'menu'   # last slide → back to menu

    # ------------------------------------------------------------------ #
    def update(self, dt: float):
        if self._fading_in:
            self._fade = min(1.0, self._fade + dt * 2.2)

    # ------------------------------------------------------------------ #
    def draw(self, surf: pygame.Surface, music_on: bool = True):
        surf.fill((0, 0, 0))

        slide = self._slides[self._idx]

        # Scale slide to fit screen, preserving aspect ratio (letterbox)
        sw, sh   = slide.get_size()
        scale    = min(S.WIDTH / sw, S.HEIGHT / sh)
        new_w    = int(sw * scale)
        new_h    = int(sh * scale)
        scaled   = pygame.transform.smoothscale(slide, (new_w, new_h))
        dest_x   = (S.WIDTH  - new_w) // 2
        dest_y   = (S.HEIGHT - new_h) // 2
        surf.blit(scaled, (dest_x, dest_y))

        # Lyric panel — dark bar at bottom
        lyrics   = _LYRICS[self._idx]
        line_h   = self._font.get_height() + 4
        panel_h  = line_h * len(lyrics) + 20
        panel    = pygame.Surface((S.WIDTH, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 185))
        surf.blit(panel, (0, S.HEIGHT - panel_h))

        for i, line in enumerate(lyrics):
            txt = self._font.render(line, True, (220, 210, 190))
            x   = S.WIDTH // 2 - txt.get_width() // 2
            y   = S.HEIGHT - panel_h + 10 + i * line_h
            surf.blit(txt, (x, y))

        # Fade overlay
        if self._fade < 1.0:
            fade_surf = pygame.Surface((S.WIDTH, S.HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(int((1.0 - self._fade) * 255))
            surf.blit(fade_surf, (0, 0))

        # Navigation hint
        total   = len(self._slides)
        dots    = '  '.join('●' if i == self._idx else '○' for i in range(total))
        nav_lbl = self._font_nav.render(dots, True, (160, 160, 160))
        surf.blit(nav_lbl, (S.WIDTH // 2 - nav_lbl.get_width() // 2, 10))

        hint_text = 'Click or Space to continue   ·   Esc to skip' if self._idx < total - 1 \
                    else 'Click or Space to begin   ·   Esc to skip'
        hint = self._font_nav.render(hint_text, True, (110, 110, 110))
        surf.blit(hint, (S.WIDTH // 2 - hint.get_width() // 2, S.HEIGHT - panel_h - 18))
