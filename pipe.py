"""
pipe.py – Pipe obstacle sprite and spawning logic.

A ``PipePair`` draws both the top and bottom pipe with cap ornaments.
The ``PipeManager`` owns a sprite group, handles spawning on a timer,
and exposes collision / scoring queries.
"""
from __future__ import annotations

import random

import pygame

import settings as S
from assets import AssetManager


# ─── PipePair ─────────────────────────────────────────────────────────────────

class PipePair(pygame.sprite.Sprite):
    """
    One obstacle consisting of a top pipe hanging from the ceiling and a
    bottom pipe rising from the ground, separated by a gap.
    """

    CAP_W   = S.PIPE_WIDTH + 12     # cap is slightly wider than body
    CAP_H   = 26

    def __init__(self, x: int, speed: float,
                 gap: int, assets: AssetManager) -> None:
        super().__init__()

        self._assets = assets
        self.speed   = speed
        self.scored  = False          # True once the bird has passed this pair

        # ── gap placement ────────────────────────────────────────────────────
        play_h    = S.SCREEN_HEIGHT - S.GROUND_HEIGHT
        max_top_h = play_h - gap - S.PIPE_MIN_HEIGHT
        top_h     = random.randint(S.PIPE_MIN_HEIGHT, max_top_h)

        self._top_h    = top_h
        self._gap      = gap
        self._bottom_y = top_h + gap

        # ── collision rects (relative to screen coords) ──────────────────────
        self._x = float(x)
        self._update_rects()

        # ── sprite surface (invisible aggregate) ─────────────────────────────
        # We don't use the sprite image for collision – we draw manually.
        self.image = pygame.Surface((S.PIPE_WIDTH, S.SCREEN_HEIGHT), pygame.SRCALPHA)
        self._render()
        self.rect  = self.image.get_rect(left=x)

    # ── public ────────────────────────────────────────────────────────────────

    def update(self) -> None:  # type: ignore[override]
        self._x         -= self.speed
        self.rect.left   = int(self._x)
        self._update_rects()

    def draw_pipes(self, surface: pygame.Surface) -> None:
        """
        Draw pipes directly onto *surface*.
        Using this instead of the sprite image gives us the cap overlap
        without requiring a surface taller than the screen.
        """
        x = int(self._x)

        # ── top pipe ──────────────────────────────────────────────────────────
        if self._top_h > 0:
            top_body = self._assets.make_pipe_body(self._top_h)
            surface.blit(top_body, (x, 0))
            # Cap sits at the bottom edge of the top pipe
            cap = self._assets.pipe_cap_surf
            cap_x = x - 6
            cap_y = self._top_h - self.CAP_H
            surface.blit(cap, (cap_x, cap_y))

        # ── bottom pipe ────────────────────────────────────────────────────────
        btm_h = S.SCREEN_HEIGHT - self._bottom_y - S.GROUND_HEIGHT
        if btm_h > 0:
            btm_body = self._assets.make_pipe_body(btm_h)
            surface.blit(btm_body, (x, self._bottom_y + self.CAP_H))
            # Cap sits at the top edge of the bottom pipe
            cap = self._assets.pipe_cap_surf
            cap_x = x - 6
            surface.blit(cap, (cap_x, self._bottom_y))

    def collides_with(self, bird_rect: pygame.Rect) -> bool:
        """Return True if the bird's collision rect overlaps either pipe."""
        return (self._top_rect.colliderect(bird_rect) or
                self._bot_rect.colliderect(bird_rect))

    @property
    def is_off_screen(self) -> bool:
        return self._x + S.PIPE_WIDTH < 0

    @property
    def right_edge(self) -> int:
        """Rightmost pixel of the pipe body (used for scoring)."""
        return int(self._x) + S.PIPE_WIDTH

    # ── private ───────────────────────────────────────────────────────────────

    def _update_rects(self) -> None:
        xi = int(self._x)
        self._top_rect = pygame.Rect(xi, 0,
                                     self.CAP_W, self._top_h)
        self._bot_rect = pygame.Rect(xi, self._bottom_y,
                                     self.CAP_W,
                                     S.SCREEN_HEIGHT - self._bottom_y)

    def _render(self) -> None:
        """
        Render a transparent placeholder for the sprite group
        (actual drawing is done in draw_pipes).
        """
        self.image.fill((0, 0, 0, 0))


# ─── PipeManager ──────────────────────────────────────────────────────────────

class PipeManager:
    """
    Spawns, updates, and removes pipe pairs; tracks current speed.

    Difficulty scales with the score:
      • pipe speed increases gradually each tick
      • spawn interval shrinks every ``SCORE_PER_DIFFICULTY_STEP`` points
    """

    def __init__(self, assets: AssetManager) -> None:
        self._assets  = assets
        self._pipes:  list[PipePair] = []
        self._speed:  float = S.PIPE_SPEED_INITIAL
        self._gap:    int   = S.PIPE_GAP
        self._last_spawn_ms: int = 0
        self._spawn_interval_ms: int = S.PIPE_SPAWN_INTERVAL_MS

    # ── interface ─────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Clear all pipes and reset difficulty."""
        self._pipes.clear()
        self._speed              = S.PIPE_SPEED_INITIAL
        self._gap                = S.PIPE_GAP
        self._last_spawn_ms      = pygame.time.get_ticks()
        self._spawn_interval_ms  = S.PIPE_SPAWN_INTERVAL_MS

    def update(self, score: int) -> int:
        """
        Advance all pipes one frame and spawn new ones when due.

        Returns the number of pipes the bird passed this frame (0 or 1).
        This value is added directly to the score by the caller.
        """
        now = pygame.time.get_ticks()

        # Spawn
        if now - self._last_spawn_ms >= self._spawn_interval_ms:
            self._pipes.append(
                PipePair(S.SCREEN_WIDTH + 10, self._speed, self._gap, self._assets)
            )
            self._last_spawn_ms = now

        # Move & prune
        self._pipes = [p for p in self._pipes if not p.is_off_screen]
        for pipe in self._pipes:
            pipe.update()

        # Ramp speed (continuous)
        self._speed = min(self._speed + S.PIPE_SPEED_INCREMENT, S.PIPE_SPEED_MAX)

        # Difficulty steps (per score milestone)
        step = score // S.SCORE_PER_DIFFICULTY_STEP
        new_interval = max(
            S.PIPE_SPAWN_INTERVAL_MIN,
            S.PIPE_SPAWN_INTERVAL_MS - step * 60,
        )
        self._spawn_interval_ms = new_interval

        # Slightly tighten gap at higher scores (floor of 130 px)
        self._gap = max(130, S.PIPE_GAP - step * 5)

        return 0  # scoring counted separately below

    def check_score(self, bird_x: int) -> int:
        """Return 1 if the bird has just cleared a pipe pair, else 0."""
        for pipe in self._pipes:
            if not pipe.scored and pipe.right_edge < bird_x:
                pipe.scored = True
                return 1
        return 0

    def check_collision(self, bird_rect: pygame.Rect) -> bool:
        """Return True if the bird's rect overlaps any pipe."""
        return any(p.collides_with(bird_rect) for p in self._pipes)

    def draw(self, surface: pygame.Surface) -> None:
        for pipe in self._pipes:
            pipe.draw_pipes(surface)

    @property
    def current_speed(self) -> float:
        return self._speed
