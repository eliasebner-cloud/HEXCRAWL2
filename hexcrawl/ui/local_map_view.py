"""Local-map placeholder view with WASD cursor on a square grid."""

from __future__ import annotations

import pygame


class LocalMapView:
    """Draws an auto-fit square grid in the map area and a clamped cursor."""

    def __init__(self, screen_width: int, screen_height: int, grid_w: int = 40, grid_h: int = 30) -> None:
        self.panel_width = 280
        self.map_width = max(200, screen_width - self.panel_width)
        self.map_height = screen_height

        self.grid_w = grid_w
        self.grid_h = grid_h

        self.cursor_x: int | None = None
        self.cursor_y: int | None = None

        self.background_color = (16, 18, 22)
        self.grid_line_color = (76, 86, 102)
        self.cursor_color = (224, 108, 117)
        self.panel_bg = (28, 32, 40)
        self.panel_text = (225, 230, 240)

        self.font = pygame.font.SysFont("consolas", 18)

    def ensure_initialized(self) -> None:
        """Initialize cursor once (first entry into Local mode)."""
        if self.cursor_x is None or self.cursor_y is None:
            self.cursor_x = self.grid_w // 2
            self.cursor_y = self.grid_h // 2

    def handle_event(self, event: pygame.event.Event) -> None:
        self.ensure_initialized()
        if event.type != pygame.KEYDOWN:
            return

        dx = 0
        dy = 0
        if event.key == pygame.K_w:
            dy = -1
        elif event.key == pygame.K_s:
            dy = 1
        elif event.key == pygame.K_a:
            dx = -1
        elif event.key == pygame.K_d:
            dx = 1

        if dx == 0 and dy == 0:
            return

        self.cursor_x = max(0, min(self.grid_w - 1, self.cursor_x + dx))
        self.cursor_y = max(0, min(self.grid_h - 1, self.cursor_y + dy))

    def update(self, dt: float) -> None:
        del dt

    def draw(self, screen: pygame.Surface, selected_world_hex: tuple[int, int] | None) -> None:
        self.ensure_initialized()
        screen.fill(self.background_color)

        cell_size = min(self.map_width / self.grid_w, self.map_height / self.grid_h)
        draw_w = cell_size * self.grid_w
        draw_h = cell_size * self.grid_h

        origin_x = (self.map_width - draw_w) / 2.0
        origin_y = (self.map_height - draw_h) / 2.0

        for gx in range(self.grid_w + 1):
            x = origin_x + gx * cell_size
            pygame.draw.line(
                screen,
                self.grid_line_color,
                (int(round(x)), int(round(origin_y))),
                (int(round(x)), int(round(origin_y + draw_h))),
                1,
            )

        for gy in range(self.grid_h + 1):
            y = origin_y + gy * cell_size
            pygame.draw.line(
                screen,
                self.grid_line_color,
                (int(round(origin_x)), int(round(y))),
                (int(round(origin_x + draw_w)), int(round(y))),
                1,
            )

        cursor_rect = pygame.Rect(
            int(round(origin_x + self.cursor_x * cell_size)),
            int(round(origin_y + self.cursor_y * cell_size)),
            max(1, int(round(cell_size))),
            max(1, int(round(cell_size))),
        )
        pygame.draw.rect(screen, self.cursor_color, cursor_rect, width=3)

        self._draw_debug_panel(screen, selected_world_hex)

    def _draw_debug_panel(
        self,
        screen: pygame.Surface,
        selected_world_hex: tuple[int, int] | None,
    ) -> None:
        panel_rect = pygame.Rect(self.map_width, 0, self.panel_width, self.map_height)
        pygame.draw.rect(screen, self.panel_bg, panel_rect)

        world_ref = selected_world_hex if selected_world_hex is not None else "(none)"
        lines = [
            "Mode: Local",
            f"cursor_x: {self.cursor_x}",
            f"cursor_y: {self.cursor_y}",
            f"grid_w: {self.grid_w}",
            f"grid_h: {self.grid_h}",
            f"Local for selected world hex: {world_ref}",
            "",
            "Controls:",
            "TAB: toggle mode",
            "ESC: quit",
            "WASD: move cursor",
        ]

        y = 18
        for line in lines:
            text_surface = self.font.render(line, True, self.panel_text)
            screen.blit(text_surface, (self.map_width + 14, y))
            y += 24
