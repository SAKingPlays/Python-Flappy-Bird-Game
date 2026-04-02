"""
background.py – Multi-layer parallax scrolling background.

Layers (back → front):
  1. Sky gradient        – static pre-baked surface
  2. Far mountains       – very slow scroll (0.3×)
  3. Near mountains      – slow scroll (0.6×)
  4. Clouds              – medium scroll (1.0×), procedural, looping
  5. Ground strip        – fast scroll (matches pipe speed)
"""
from __future__ import annotations

import math
import random

import pygame

import settings as S
from assets import AssetManager


# ─── Cloud ────────────────────────────────────────────────────────────────────

class Cloud:
    """A single fluffy cloud that drifts left and wraps around."""

    def __init__(self, x: float | None = None) -> None:
        self._reset(x)

    def _reset(self, x: float | None = None) -> None:
        self.x   = float(x) if x is not None else float(S.SCREEN_WIDTH + random.randint(0, 300))
        self.y   = random.randint(30, S.SCREEN_HEIGHT // 3)
        self.w   = random.randint(80, 160)
        self.h   = random.randint(30, 55)
        self.spd = random.uniform(0.55, 1.10)

    def update(self) -> None:
        self.x -= self.spd
        if self.x + self.w < 0:
            self._reset()

    def draw(self, surface: pygame.Surface) -> None:
        _draw_cloud(surface, int(self.x), int(self.y), self.w, self.h)


def _draw_cloud(surface: pygame.Surface, x: int, y: int, w: int, h: int) -> None:
    """Draw a multi-ellipse cloud puff directly onto *surface*."""
    puffs = [
        (x,              y + h // 4,  w // 2, h // 2),
        (x + w // 4,     y,           w // 2, h // 2 + 4),
        (x + w // 2,     y + h // 4,  w // 2, h // 2),
        (x + w // 5,     y + h // 3,  w * 3 // 5, h // 3),
    ]
    shadow_puffs = [(px, py + 4, pw, ph) for px, py, pw, ph in puffs]
    for rect in shadow_puffs:
        pygame.draw.ellipse(surface, S.CLOUD_SHADOW, rect)
    for rect in puffs:
        pygame.draw.ellipse(surface, S.CLOUD_COLOR, rect)


# ─── Background ──────────────────────────────────────────────────────────────

class Background:
    """
    Owns all background layers and advances their scroll offsets each frame.

    Call ``update(pipe_speed)`` every frame while playing, then ``draw(surface)``.
    """

    # Parallax multipliers (relative to pipe speed)
    _MTN_FAR_SPEED  = 0.07
    _MTN_NEAR_SPEED = 0.18

    def __init__(self, assets: AssetManager) -> None:
        self._assets = assets

        # Scroll offsets (pixels shifted left)
        self._mtn_far_x:  float = 0.0
        self._mtn_near_x: float = 0.0
        self._ground_x:   float = 0.0

        # Cloud objects
        self._clouds: list[Cloud] = [
            Cloud(x=random.randint(-200, S.SCREEN_WIDTH)) for _ in range(6)
        ]

        # Mountain layer dimensions
        self._mtn_far_surf  = assets.mountain_far
        self._mtn_near_surf = assets.mountain_near
        mtn_h = S.SCREEN_HEIGHT // 3

        # Bottom-anchored Y positions for mountain layers
        ground_top = S.SCREEN_HEIGHT - S.GROUND_HEIGHT
        self._mtn_far_y  = ground_top - mtn_h + 10
        self._mtn_near_y = ground_top - mtn_h // 2 - 20 + 10

    # ── interface ─────────────────────────────────────────────────────────────

    def update(self, pipe_speed: float = S.PIPE_SPEED_INITIAL) -> None:
        """Advance all layer scroll positions by one frame."""
        self._mtn_far_x  = (self._mtn_far_x  + pipe_speed * self._MTN_FAR_SPEED)  % S.SCREEN_WIDTH
        self._mtn_near_x = (self._mtn_near_x + pipe_speed * self._MTN_NEAR_SPEED) % S.SCREEN_WIDTH
        self._ground_x   = (self._ground_x   + pipe_speed) % S.SCREEN_WIDTH

        for cloud in self._clouds:
            cloud.update()

    def draw(self, surface: pygame.Surface) -> None:
        """Render all layers back-to-front onto *surface*."""
        # 1 – Sky (pre-baked, no scroll)
        surface.blit(self._assets.sky, (0, 0))

        # 2 – Far mountains (tiled horizontally)
        self._blit_tiled(surface, self._mtn_far_surf,
                         -int(self._mtn_far_x), self._mtn_far_y)

        # 3 – Near mountains
        self._blit_tiled(surface, self._mtn_near_surf,
                         -int(self._mtn_near_x), self._mtn_near_y)

        # 4 – Clouds
        for cloud in self._clouds:
            cloud.draw(surface)

        # 5 – Ground (tiled)
        gx = -int(self._ground_x)
        gy = S.SCREEN_HEIGHT - S.GROUND_HEIGHT
        self._blit_tiled(surface, self._assets.ground_tile, gx, gy)

    def reset(self) -> None:
        """Reset all offsets (new game)."""
        self._mtn_far_x  = 0.0
        self._mtn_near_x = 0.0
        self._ground_x   = 0.0

    # ── private ───────────────────────────────────────────────────────────────

    @staticmethod
    def _blit_tiled(surface: pygame.Surface, tile: pygame.Surface,
                    x: int, y: int) -> None:
        """Blit *tile* repeatedly in X to fill the screen width."""
        tw = tile.get_width()
        # Normalise offset into [0, tw)
        x = x % tw
        if x > 0:
            x -= tw
        cx = x
        while cx < S.SCREEN_WIDTH:
            surface.blit(tile, (cx, y))
            cx += tw
