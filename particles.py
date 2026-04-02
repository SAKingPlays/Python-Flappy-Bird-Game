"""
particles.py – Lightweight particle system.

Two emitter helpers are exposed:
    emit_flap(system, x, y)  – feather/dust puff on wing beat
    emit_crash(system, x, y) – explosive burst on collision
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List

import pygame

import settings as S


@dataclass
class Particle:
    """A single particle with position, velocity, and remaining life."""
    x:      float
    y:      float
    vx:     float
    vy:     float
    radius: float
    colour: tuple
    life:   int          # frames remaining
    max_life: int = field(init=False)
    alpha:  float = 255.0

    def __post_init__(self) -> None:
        self.max_life = self.life

    # ─────────────────────────────────────────────────────────────────────────

    def update(self) -> bool:
        """Advance one frame.  Returns True while the particle is still alive."""
        self.vy += S.PARTICLE_GRAVITY
        self.x  += self.vx
        self.y  += self.vy
        self.life -= 1
        self.alpha = 255.0 * (self.life / self.max_life)
        return self.life > 0

    def draw(self, surface: pygame.Surface) -> None:
        if self.radius < 1:
            return
        r = int(self.radius * (self.life / self.max_life))
        if r < 1:
            return
        tmp = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        a   = max(0, min(255, int(self.alpha)))
        pygame.draw.circle(tmp, (*self.colour, a), (r, r), r)
        surface.blit(tmp, (int(self.x) - r, int(self.y) - r))


# ─── ParticleSystem ───────────────────────────────────────────────────────────

class ParticleSystem:
    """Manages a pool of active particles."""

    def __init__(self) -> None:
        self._particles: List[Particle] = []

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def update(self) -> None:
        self._particles = [p for p in self._particles if p.update()]

    def draw(self, surface: pygame.Surface) -> None:
        for p in self._particles:
            p.draw(surface)

    def clear(self) -> None:
        self._particles.clear()

    # ── emitters ──────────────────────────────────────────────────────────────

    def emit_flap(self, x: float, y: float) -> None:
        """Small feather-puff emitted every time the bird flaps."""
        for _ in range(S.FLAP_PARTICLE_COUNT):
            angle = random.uniform(math.pi * 0.6, math.pi * 1.4)  # leftward arc
            speed = random.uniform(1.5, 3.5)
            self._particles.append(Particle(
                x=x - 8,
                y=y + random.uniform(-6, 6),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 1.5,
                radius=random.uniform(2.5, 5.0),
                colour=random.choice(S.PARTICLE_FLAP_COLORS),
                life=random.randint(18, 30),
            ))

    def emit_crash(self, x: float, y: float) -> None:
        """Explosive burst on collision."""
        for _ in range(S.CRASH_PARTICLE_COUNT):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.0, 6.5)
            self._particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 2.0,
                radius=random.uniform(3.0, 8.0),
                colour=random.choice(S.PARTICLE_CRASH_COLORS),
                life=random.randint(25, 50),
            ))
