"""
ui.py – All user-interface rendering.

Keeps every draw-call for menus, HUD, and overlays in one place so that
game.py stays focused purely on state-machine logic.

Public helpers
──────────────
    render_text(surface, text, font, color, cx, cy, shadow=True)
    draw_menu(surface, fonts, high_score, tick)
    draw_hud(surface, fonts, score, high_score, paused=False)
    draw_pause_overlay(surface, fonts)
    draw_game_over(surface, fonts, score, high_score, alpha)
    draw_get_ready(surface, fonts, alpha)
"""
from __future__ import annotations

import math

import pygame

import settings as S


# ─── primitive helpers ────────────────────────────────────────────────────────

def render_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple,
    cx: int,
    cy: int,
    shadow: bool = True,
    shadow_offset: int = 2,
    shadow_color: tuple = S.SHADOW_COLOR,
    alpha: int = 255,
) -> pygame.Rect:
    """
    Blit centred text onto *surface*, with an optional drop shadow.
    Returns the bounding rect of the rendered text.
    """
    if shadow:
        shadow_surf = font.render(text, True, shadow_color)
        shadow_surf.set_alpha(alpha)
        sr = shadow_surf.get_rect(center=(cx + shadow_offset, cy + shadow_offset))
        surface.blit(shadow_surf, sr)

    txt_surf = font.render(text, True, color)
    txt_surf.set_alpha(alpha)
    tr = txt_surf.get_rect(center=(cx, cy))
    surface.blit(txt_surf, tr)
    return tr


def _draw_panel(surface: pygame.Surface, rect: pygame.Rect,
                radius: int = 12, alpha: int = 195) -> None:
    """Rounded-rectangle semi-transparent panel."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*S.PANEL_BG[:3], alpha), panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, (*S.WHITE, 60), panel.get_rect(), width=2, border_radius=radius)
    surface.blit(panel, rect.topleft)


def _pulsing_scale(tick: int, period: int = 80, depth: float = 0.06) -> float:
    """Return a scale factor that oscillates gently – good for breathing animations."""
    return 1.0 + math.sin(tick * math.pi * 2 / period) * depth


# ─── Medal helper ─────────────────────────────────────────────────────────────

def _medal_color(score: int) -> tuple | None:
    if score >= 40:
        return S.GOLD_MEDAL
    elif score >= 20:
        return S.SILVER_MEDAL
    elif score >= 10:
        return S.BRONZE_MEDAL
    return None


def _draw_medal(surface: pygame.Surface, score: int, cx: int, cy: int) -> None:
    colour = _medal_color(score)
    if colour is None:
        return
    pygame.draw.circle(surface, colour, (cx, cy), 18)
    pygame.draw.circle(surface, S.WHITE, (cx, cy), 18, 2)
    pygame.draw.circle(surface, (*colour[:3],), (cx - 5, cy - 5), 6)


# ─── Screens ──────────────────────────────────────────────────────────────────

def draw_menu(
    surface: pygame.Surface,
    fonts: dict,
    high_score: int,
    tick: int,
) -> None:
    """Animated main-menu screen."""
    W, H = S.SCREEN_WIDTH, S.SCREEN_HEIGHT
    cx   = W // 2

    # ── title ─────────────────────────────────────────────────────────────────
    scale = _pulsing_scale(tick, period=90, depth=0.04)
    title_font = fonts["huge"]
    title_surf = title_font.render("FLAPPY", True, S.SCORE_GOLD)
    sub_surf   = title_font.render("BIRD",   True, S.WHITE)

    tw = int(title_surf.get_width() * scale)
    th = int(title_surf.get_height() * scale)
    title_surf_s = pygame.transform.smoothscale(title_surf, (tw, th))
    sub_surf_s   = pygame.transform.smoothscale(sub_surf,   (tw, th))

    # Shadow
    sh = fonts["huge"].render("FLAPPY", True, S.SHADOW_COLOR)
    sh = pygame.transform.smoothscale(sh, (tw, th))
    surface.blit(sh, sh.get_rect(center=(cx + 3, H // 4 + 3)))
    surface.blit(title_surf_s, title_surf_s.get_rect(center=(cx, H // 4)))

    sh2 = fonts["huge"].render("BIRD", True, S.SHADOW_COLOR)
    sh2 = pygame.transform.smoothscale(sh2, (tw, th))
    surface.blit(sh2, sh2.get_rect(center=(cx + 3, H // 4 + th + 3)))
    surface.blit(sub_surf_s, sub_surf_s.get_rect(center=(cx, H // 4 + th)))

    # ── controls ──────────────────────────────────────────────────────────────
    ctrl_y = H // 2 + 10
    panel_rect = pygame.Rect(cx - 120, ctrl_y - 10, 240, 100)
    _draw_panel(surface, panel_rect)

    render_text(surface, "PRESS  SPACE  to Start",  fonts["small"], S.WHITE,      cx, ctrl_y + 20)
    render_text(surface, "CLICK  /  TAP to Flap",   fonts["tiny"],  (200,200,200), cx, ctrl_y + 50)
    render_text(surface, "P  to Pause",             fonts["tiny"],  (200,200,200), cx, ctrl_y + 72)

    # ── high score ────────────────────────────────────────────────────────────
    if high_score > 0:
        hs_y = H * 3 // 4
        render_text(surface, f"Best: {high_score}", fonts["medium"], S.SCORE_GOLD, cx, hs_y)

    # ── bottom hint ───────────────────────────────────────────────────────────
    blink_alpha = int(155 + 100 * math.sin(tick * 0.12))
    render_text(surface, "Q  to Quit", fonts["tiny"], S.WHITE, cx, H - 40,
                shadow=False, alpha=blink_alpha)


def draw_hud(
    surface: pygame.Surface,
    fonts: dict,
    score: int,
    high_score: int,
    paused: bool = False,
) -> None:
    """Score counter shown during active play (and while paused)."""
    cx = S.SCREEN_WIDTH // 2

    # Main score – large, centred near top
    render_text(surface, str(score), fonts["large"], S.WHITE, cx, 52,
                shadow_offset=3)

    # Best score – small, top-right
    if high_score > 0:
        hs_text = f"Best {high_score}"
        render_text(surface, hs_text, fonts["tiny"], (220, 220, 220),
                    S.SCREEN_WIDTH - 60, 20, shadow=True, shadow_offset=1)


def draw_pause_overlay(surface: pygame.Surface, fonts: dict) -> None:
    """Darken the screen and show a PAUSED banner."""
    W, H = S.SCREEN_WIDTH, S.SCREEN_HEIGHT
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 130))
    surface.blit(overlay, (0, 0))

    panel = pygame.Rect(W // 2 - 130, H // 2 - 70, 260, 140)
    _draw_panel(surface, panel, alpha=220)

    render_text(surface, "PAUSED", fonts["large"], S.WHITE, W // 2, H // 2 - 28)
    render_text(surface, "Press P or ESC to Resume", fonts["tiny"],
                (200, 200, 200), W // 2, H // 2 + 18)
    render_text(surface, "SPACE to Restart", fonts["tiny"],
                (200, 200, 200), W // 2, H // 2 + 44)


def draw_game_over(
    surface: pygame.Surface,
    fonts: dict,
    score: int,
    high_score: int,
    alpha: int,
    new_best: bool,
) -> None:
    """Animated game-over panel that fades in."""
    W, H = S.SCREEN_WIDTH, S.SCREEN_HEIGHT
    cx   = W // 2

    # Full-screen dim overlay (fades in with alpha)
    overlay = pygame.Surface((W, H))
    overlay.fill(S.OVERLAY_CLR)
    overlay.set_alpha(min(alpha // 2, 120))
    surface.blit(overlay, (0, 0))

    # Wait for the overlay to be at least half-visible before showing text
    if alpha < 60:
        return

    panel_h = 260
    panel   = pygame.Rect(cx - 145, H // 2 - panel_h // 2 - 20, 290, panel_h)
    _draw_panel(surface, panel, radius=16, alpha=min(alpha, 210))

    # Title
    render_text(surface, "GAME OVER", fonts["large"], (255, 90, 90),
                cx, H // 2 - 90, shadow_offset=3, alpha=alpha)

    # Scores
    render_text(surface, f"Score:  {score}", fonts["medium"], S.WHITE,
                cx, H // 2 - 38, alpha=alpha)

    if new_best:
        render_text(surface, "🏆  NEW BEST!", fonts["small"], S.SCORE_GOLD,
                    cx, H // 2 - 5, alpha=alpha)
    else:
        render_text(surface, f"Best:  {high_score}", fonts["small"], (200, 200, 200),
                    cx, H // 2 - 5, alpha=alpha)

    # Medal
    _draw_medal(surface, score, cx - 95, H // 2 + 45)

    # Grade text
    grade_map = [(40, "S"), (20, "A"), (10, "B"), (0, "C")]
    grade = next(g for limit, g in grade_map if score >= limit)
    grade_color = {
        "S": S.SCORE_GOLD,
        "A": (100, 220, 100),
        "B": (100, 180, 255),
        "C": (200, 200, 200),
    }[grade]
    render_text(surface, grade, fonts["large"], grade_color,
                cx + 65, H // 2 + 45, alpha=alpha)

    # Buttons
    if alpha >= 200:
        render_text(surface, "SPACE / Click  –  Restart", fonts["tiny"],
                    (220, 220, 220), cx, H // 2 + 90)
        render_text(surface, "Q  –  Quit", fonts["tiny"],
                    (180, 180, 180), cx, H // 2 + 112)


def draw_get_ready(surface: pygame.Surface, fonts: dict, alpha: int) -> None:
    """Brief 'Get Ready!' flash at the start of each game."""
    render_text(surface, "Get Ready!", fonts["medium"], S.SCORE_GOLD,
                S.SCREEN_WIDTH // 2, S.SCREEN_HEIGHT // 3, alpha=alpha)
