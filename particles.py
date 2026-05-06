import random, math
import pygame


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'radius', 'color', 'gravity')

    def __init__(self, x, y, color, speed=180, radius=5, life=0.6, gravity=0.0):
        angle = random.uniform(0, math.tau)
        spd   = random.uniform(speed * 0.4, speed)
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = math.cos(angle) * spd, math.sin(angle) * spd
        self.radius   = radius
        self.color    = color
        self.life     = life
        self.max_life = life
        self.gravity  = gravity

    def update(self, dt):
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt
        self.vx  *= (1 - 3 * dt)
        self.vy  *= (1 - 3 * dt)

    @property
    def alive(self):
        return self.life > 0

    def draw(self, surf, offset=(0, 0)):
        alpha = max(0, self.life / self.max_life)
        r = int(self.radius * (0.4 + 0.6 * alpha))
        if r < 1:
            return
        color = (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha),
        )
        pygame.draw.circle(surf, color,
                           (int(self.x + offset[0]), int(self.y + offset[1])), r)


class ParticleSystem:
    def __init__(self):
        self._particles: list[Particle] = []

    def explosion(self, x, y, color, count=20, speed=220, radius=6, life=0.55):
        for _ in range(count):
            self._particles.append(Particle(x, y, color, speed, radius, life, gravity=120))

    def sparks(self, x, y, color=(255, 240, 120), count=8):
        for _ in range(count):
            self._particles.append(Particle(x, y, color, speed=300, radius=3, life=0.3))

    def update(self, dt):
        self._particles = [p for p in self._particles if p.alive]
        for p in self._particles:
            p.update(dt)

    def draw(self, surf, offset=(0, 0)):
        for p in self._particles:
            p.draw(surf, offset)
