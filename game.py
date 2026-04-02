"""
game.py – Top-level game orchestrator.

State machine
─────────────
  MENU      → PLAYING  on Space / click
  PLAYING   → PAUSED   on P / Esc
              GAME_OVER on collision or boundary
  PAUSED    → PLAYING  on P / Esc / Space
  GAME_OVER → PLAYING  on Space / click (restart)

Screen-shake and fade-in transitions are handled here rather than in ui.py
because they are game-level effects that span multiple systems.
"""
from __future__ import annotations

import random
import sys

import pygame
from pygame.locals import (
    QUIT, KEYDOWN, MOUSEBUTTONDOWN,
    K_SPACE, K_p, K_ESCAPE, K_q, K_r,
)

import settings as S
from settings import GameState
from assets import AssetManager
from background import Background
from bird import Bird
from pipe import PipeManager
from particles import ParticleSystem
from highscore import load_high_score, save_high_score
import ui


class Game:
    """
    Owns the pygame window, clock, and every subsystem.
    Call ``run()`` to enter the main loop.
    """

    def __init__(self) -> None:
        # ── display ───────────────────────────────────────────────────────────
        self._screen = pygame.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
        pygame.display.set_caption(S.TITLE)

        # Off-screen surface that receives all drawing; the screen only gets the
        # final blit (possibly offset for screen-shake).
        self._canvas = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))

        self._clock = pygame.time.Clock()
        self._tick  = 0   # global frame counter

        # ── assets (must come after pygame.init) ─────────────────────────────
        self._assets = AssetManager()

        # ── persistent data ───────────────────────────────────────────────────
        self._high_score: int  = load_high_score()
        self._new_best:   bool = False

        # ── subsystems ────────────────────────────────────────────────────────
        self._particles  = ParticleSystem()
        self._background = Background(self._assets)
        self._pipes      = PipeManager(self._assets)

        # Bird and score are initialised (or re-initialised) by _reset_game()
        self._bird:  Bird | None = None
        self._score: int = 0

        # ── state machine ─────────────────────────────────────────────────────
        self._state: GameState = GameState.MENU

        # ── screen-shake ──────────────────────────────────────────────────────
        self._shake_frames: int = 0

        # ── game-over fade ────────────────────────────────────────────────────
        self._go_alpha: int = 0    # 0 → 255

        # ── get-ready flash ───────────────────────────────────────────────────
        self._ready_alpha: int = 255
        self._ready_visible: bool = False

    # ─── main loop ────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Enter the game loop.  Does not return until the window is closed."""
        while True:
            events = self._poll_events()
            self._update(events)
            self._draw()
            self._clock.tick(S.FPS)
            self._tick += 1

    # ─── event polling ────────────────────────────────────────────────────────

    def _poll_events(self) -> list[pygame.event.Event]:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                self._quit()
        return events

    # ─── update dispatch ──────────────────────────────────────────────────────

    def _update(self, events: list[pygame.event.Event]) -> None:
        match self._state:
            case GameState.MENU:
                self._update_menu(events)
            case GameState.PLAYING:
                self._update_playing(events)
            case GameState.PAUSED:
                self._update_paused(events)
            case GameState.GAME_OVER:
                self._update_game_over(events)

        # Always tick the background (gives life to clouds in menu / game-over)
        speed = self._pipes.current_speed if self._state == GameState.PLAYING else S.PIPE_SPEED_INITIAL
        self._background.update(speed)

    # ─── draw dispatch ────────────────────────────────────────────────────────

    def _draw(self) -> None:
        # Draw everything onto the off-screen canvas
        match self._state:
            case GameState.MENU:
                self._draw_menu()
            case GameState.PLAYING:
                self._draw_playing()
            case GameState.PAUSED:
                self._draw_playing()
                ui.draw_pause_overlay(self._canvas, self._assets.fonts)
            case GameState.GAME_OVER:
                self._draw_playing()
                ui.draw_game_over(
                    self._canvas, self._assets.fonts,
                    self._score, self._high_score,
                    self._go_alpha, self._new_best,
                )

        # Apply screen-shake by blitting the canvas with a random offset
        ox, oy = self._shake_offset()
        self._screen.blit(self._canvas, (ox, oy))
        pygame.display.flip()

    # ─── MENU state ──────────────────────────────────────────────────────────

    def _update_menu(self, events: list) -> None:
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self._start_game()
                elif event.key == K_q:
                    self._quit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                self._start_game()

    def _draw_menu(self) -> None:
        self._background.draw(self._canvas)
        # Draw an idle bird in the centre for decoration
        if self._bird:
            self._bird.update()
            self._canvas.blit(self._bird.image, self._bird.rect)
        ui.draw_menu(self._canvas, self._assets.fonts, self._high_score, self._tick)

    # ─── PLAYING state ───────────────────────────────────────────────────────

    def _update_playing(self, events: list) -> None:
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self._flap()
                elif event.key in (K_p, K_ESCAPE):
                    self._state = GameState.PAUSED
                elif event.key == K_q:
                    self._quit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                self._flap()

        if not self._bird:
            return

        # Physics
        self._bird.update()
        self._pipes.update(self._score)
        self._particles.update()

        # ── get-ready fade-out ────────────────────────────────────────────────
        if self._ready_visible:
            self._ready_alpha -= 6
            if self._ready_alpha <= 0:
                self._ready_alpha   = 0
                self._ready_visible = False

        # ── scoring ───────────────────────────────────────────────────────────
        gained = self._pipes.check_score(self._bird.x)
        if gained:
            self._score += gained
            self._assets.play("score")
            if self._score > self._high_score:
                self._high_score = self._score
                self._new_best   = True

        # ── collision / boundary check ────────────────────────────────────────
        hit_pipe   = self._pipes.check_collision(self._bird.collision_rect)
        hit_ground = self._bird.y >= S.SCREEN_HEIGHT - S.GROUND_HEIGHT - S.BIRD_RADIUS
        hit_ceil   = self._bird.y <= S.BIRD_RADIUS

        if hit_pipe or hit_ground:
            self._trigger_death()

    def _draw_playing(self) -> None:
        self._background.draw(self._canvas)
        self._pipes.draw(self._canvas)
        self._particles.draw(self._canvas)
        if self._bird:
            self._canvas.blit(self._bird.image, self._bird.rect)
        ui.draw_hud(self._canvas, self._assets.fonts,
                    self._score, self._high_score,
                    paused=(self._state == GameState.PAUSED))
        if self._ready_visible:
            ui.draw_get_ready(self._canvas, self._assets.fonts, self._ready_alpha)

    # ─── PAUSED state ────────────────────────────────────────────────────────

    def _update_paused(self, events: list) -> None:
        for event in events:
            if event.type == KEYDOWN:
                if event.key in (K_p, K_ESCAPE, K_space := K_SPACE):
                    self._state = GameState.PLAYING
                elif event.key == K_r:
                    self._start_game()
                elif event.key == K_q:
                    self._quit()

    # ─── GAME OVER state ─────────────────────────────────────────────────────

    def _update_game_over(self, events: list) -> None:
        # Advance bird physics (falls onto ground) and particles
        if self._bird:
            self._bird.update()
        self._particles.update()

        # Advance shake decay
        if self._shake_frames > 0:
            self._shake_frames -= 1

        # Fade-in game-over panel
        self._go_alpha = min(self._go_alpha + 5, 255)

        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_SPACE and self._go_alpha >= 200:
                    self._start_game()
                elif event.key == K_q:
                    self._quit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self._go_alpha >= 200:
                    self._start_game()

    # ─── helpers ─────────────────────────────────────────────────────────────

    def _start_game(self) -> None:
        """Initialise (or re-initialise) all mutable game state."""
        self._score         = 0
        self._new_best      = False
        self._go_alpha      = 0
        self._shake_frames  = 0
        self._ready_alpha   = 255
        self._ready_visible = True

        self._particles.clear()
        self._pipes.reset()
        self._background.reset()

        self._bird  = Bird(self._assets, self._particles)
        self._state = GameState.PLAYING

    def _flap(self) -> None:
        if self._bird and self._bird.alive:
            self._bird.flap()

    def _trigger_death(self) -> None:
        """Handle the moment of collision: play sounds, shake, save score."""
        if not self._bird or not self._bird.alive:
            return
        self._bird.kill_bird()
        self._assets.play("hit")
        pygame.time.delay(80)       # brief pause for impact feel
        self._assets.play("die")
        self._shake_frames = S.SHAKE_DURATION
        save_high_score(self._score)
        self._state = GameState.GAME_OVER

    def _shake_offset(self) -> tuple[int, int]:
        """Return a random pixel offset for screen-shake; (0, 0) when calm."""
        if self._shake_frames <= 0:
            return (0, 0)
        intensity = int(S.SHAKE_INTENSITY * (self._shake_frames / S.SHAKE_DURATION))
        return (
            random.randint(-intensity, intensity),
            random.randint(-intensity, intensity),
        )

    @staticmethod
    def _quit() -> None:
        pygame.quit()
        sys.exit()
