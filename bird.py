"""
bird.py – Player-controlled bird sprite.

Physics model
─────────────
  velocity  += GRAVITY   each frame (terminal-clamped)
  y         += velocity
  velocity   = JUMP_VELOCITY on flap

Rotation is smoothly interpolated towards a target angle derived from
the current vertical velocity, giving the classic Flappy Bird "tilt".

Wing animation cycles through three pre-rendered frames stored in
AssetManager.bird_frames.  Flapping triggers a rapid cycle; gliding
cycles slowly to give a subtle idle animation.
"""
from __future__ import annotations

import pygame

import settings as S
from assets import AssetManager
from particles import ParticleSystem


class Bird(pygame.sprite.Sprite):
    """Represents the player-controlled bird."""

    # Frame cycling constants
    _FLAP_ANIM_RATE  = 4   # ticks per frame during an active flap
    _IDLE_ANIM_RATE  = 10  # ticks per frame during idle glide

    def __init__(self, assets: AssetManager, particles: ParticleSystem) -> None:
        super().__init__()

        self._assets    = assets
        self._particles = particles

        # ── sprite state ──────────────────────────────────────────────────────
        self._frame_idx:    int   = 0
        self._anim_tick:    int   = 0
        self._flap_active:  bool  = False    # currently in a flap cycle
        self._flap_tick:    int   = 0

        # ── physics ───────────────────────────────────────────────────────────
        self.y:        float = float(S.SCREEN_HEIGHT // 2)
        self.velocity: float = 0.0
        self._rotation: float = 0.0          # current visual rotation (degrees)

        # ── status ────────────────────────────────────────────────────────────
        self.alive: bool = True

        # ── pygame.sprite.Sprite required attributes ──────────────────────────
        self.image: pygame.Surface = assets.bird_frames[0]
        self.rect:  pygame.Rect    = self.image.get_rect(
            center=(S.BIRD_X, int(self.y))
        )

    # ── public interface ──────────────────────────────────────────────────────

    def flap(self) -> None:
        """Impulse an upward jump and start wing-flap animation + particles."""
        if not self.alive:
            return
        self.velocity     = S.JUMP_VELOCITY
        self._flap_active = True
        self._flap_tick   = 0
        self._particles.emit_flap(S.BIRD_X, self.y)
        self._assets.play("flap")

    def update(self) -> None:  # type: ignore[override]
        """Advance physics, rotation, and animation by one frame."""
        self._apply_physics()
        self._update_rotation()
        self._advance_animation()
        self._update_sprite()

    def kill_bird(self) -> None:
        """Mark the bird as dead (it will continue to fall for visual effect)."""
        self.alive = False
        self._particles.emit_crash(S.BIRD_X, self.y)

    @property
    def collision_rect(self) -> pygame.Rect:
        """Slightly inset rect for fairer collision detection."""
        return self.rect.inflate(-10, -10)

    @property
    def x(self) -> int:
        return S.BIRD_X

    # ── private helpers ───────────────────────────────────────────────────────

    def _apply_physics(self) -> None:
        self.velocity = min(self.velocity + S.GRAVITY, S.TERMINAL_VELOCITY)
        self.y       += self.velocity

        # Clamp inside playfield while alive
        if self.alive:
            top    = float(S.BIRD_RADIUS)
            bottom = float(S.SCREEN_HEIGHT - S.GROUND_HEIGHT - S.BIRD_RADIUS)
            if self.y < top:
                self.y        = top
                self.velocity = 0.0
            elif self.y > bottom:
                self.y        = bottom
                self.velocity = 0.0

    def _update_rotation(self) -> None:
        """Smoothly tilt the bird based on velocity."""
        # Target: nose-up on ascent, steep nose-down on descent
        target = max(-28.0, min(70.0, self.velocity * -3.2))
        # Exponential smoothing
        self._rotation += (target - self._rotation) * 0.20

    def _advance_animation(self) -> None:
        n = S.BIRD_FRAME_COUNT
        if self._flap_active:
            self._flap_tick += 1
            self._frame_idx  = min(self._flap_tick // self._FLAP_ANIM_RATE, n - 1)
            if self._flap_tick >= n * self._FLAP_ANIM_RATE:
                self._flap_active = False
                self._flap_tick   = 0
        else:
            self._anim_tick += 1
            if self._anim_tick >= self._IDLE_ANIM_RATE * n:
                self._anim_tick = 0
            self._frame_idx = self._anim_tick // self._IDLE_ANIM_RATE

    def _update_sprite(self) -> None:
        """Rotate the current frame and update the sprite rect."""
        raw      = self._assets.bird_frames[self._frame_idx]
        # pygame.transform.rotate: +angle ≡ counter-clockwise
        rotated  = pygame.transform.rotate(raw, self._rotation)
        self.image = rotated
        self.rect  = rotated.get_rect(center=(S.BIRD_X, int(self.y)))
