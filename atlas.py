"""LibGDX .atlas parser — returns cropped pygame Surfaces."""
import os
import pygame


def load_atlas(atlas_path: str, scale: float = 1.0) -> dict[str, list[pygame.Surface]]:
    """Parse a LibGDX atlas file and return {name: [frame0, frame1, ...]}."""
    sprites: dict[str, list[tuple[int, pygame.Surface]]] = {}
    pages: dict[str, tuple[pygame.Surface, int]] = {}  # filename -> (surface, height)

    current_page_file = None
    current_page_height = 0
    current_name = None
    props: dict = {}

    with open(atlas_path) as f:
        for raw in f:
            line = raw.rstrip('\n')
            if not line.strip():
                continue

            if ':' not in line and not line.startswith(' ') and not line.startswith('\t'):
                # New page declaration
                fname = line.strip()
                page_path = os.path.join(os.path.dirname(atlas_path), fname)
                if os.path.exists(page_path):
                    surf = pygame.image.load(page_path).convert_alpha()
                    current_page_height = surf.get_height()
                    pages[fname] = (surf, current_page_height)
                    current_page_file = fname
                continue

            stripped = line.strip()
            if ':' in stripped:
                key, _, val = stripped.partition(':')
                key = key.strip()
                val = val.strip()

                if key == 'size' and current_name is None:
                    h = int(val.split(',')[1].strip())
                    if current_page_file:
                        pg, _ = pages.get(current_page_file, (None, 0))
                        if pg:
                            pages[current_page_file] = (pg, h)
                            current_page_height = h
                    continue

                if current_name:
                    props[key] = val
            else:
                # New sprite name
                if current_name and current_page_file and current_page_file in pages:
                    _commit(sprites, current_name, props, pages, current_page_file)
                current_name = stripped
                props = {}

    if current_name and current_page_file and current_page_file in pages:
        _commit(sprites, current_name, props, pages, current_page_file)

    result: dict[str, list[pygame.Surface]] = {}
    for name, indexed in sprites.items():
        indexed.sort(key=lambda t: t[0])
        frames = [t[1] for t in indexed]
        if scale != 1.0:
            frames = [
                pygame.transform.scale(f, (int(f.get_width() * scale), int(f.get_height() * scale)))
                for f in frames
            ]
        result[name] = frames

    return result


def _commit(sprites, name, props, pages, page_file):
    page_surf, page_h = pages[page_file]
    try:
        x, y   = [int(v.strip()) for v in props['xy'].split(',')]
        w, h   = [int(v.strip()) for v in props['size'].split(',')]
        index  = int(props.get('index', '-1'))
        region = page_surf.subsurface(pygame.Rect(x, y, w, h))
        crop = region.copy()
        sprites.setdefault(name, []).append((index, crop))
    except (KeyError, ValueError):
        pass
