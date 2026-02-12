"""Local-map placeholder rendering with square grid and WASD cursor."""

from __future__ import annotations

import pygame


class LocalMapView:
    """Renders a square local grid placeholder in the left map area."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.panel_width = 280
        self.map_width = max(200, screen_width - self.panel_width)
        self.map_height = screen_height

        self.grid_w = 40
        self.grid_h = 30
        self.cursor_x = self.grid_w // 2
        self.cursor_y = self.grid_h // 2

        self.background_color = (16, 18, 22)
        self.grid_line_color = (88, 98, 116)
        self.cursor_color = (224, 188, 92)
        self.panel_bg = (28, 32, 40)
        self.panel_text = (225, 230, 240)

        self.font = pygame.font.SysFont("consolas", 18)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_w:
            self.cursor_y -= 1
        elif event.key == pygame.K_s:
            self.cursor_y += 1
        elif event.key == pygame.K_a:
            self.cursor_x -= 1
        elif event.key == pygame.K_d:
            self.cursor_x += 1

        self.cursor_x = max(0, min(self.grid_w - 1, self.cursor_x))
        self.cursor_y = max(0, min(self.grid_h - 1, self.cursor_y))

    def update(self, dt: float) -> None:
        del dt

    def draw(self, screen: pygame.Surface, selected_world_hex: tuple[int, int] | None) -> None:
        screen.fill(self.background_color)
        self._draw_grid(screen)
        self._draw_debug_panel(screen, selected_world_hex)

    def _draw_grid(self, screen: pygame.Surface) -> None:
        cell_size = min(self.map_width / self.grid_w, self.map_height / self.grid_h)
        grid_pixel_w = cell_size * self.grid_w
        grid_pixel_h = cell_size * self.grid_h
        origin_x = (self.map_width - grid_pixel_w) / 2.0
        origin_y = (self.map_height - grid_pixel_h) / 2.0

        for gx in range(self.grid_w + 1):
            x = origin_x + gx * cell_size
            pygame.draw.line(
                screen,
                self.grid_line_color,
                (round(x), round(origin_y)),
                (round(x), round(origin_y + grid_pixel_h)),
                width=1,
            )

        for gy in range(self.grid_h + 1):
            y = origin_y + gy * cell_size
            pygame.draw.line(
                screen,
                self.grid_line_color,
                (round(origin_x), round(y)),
                (round(origin_x + grid_pixel_w), round(y)),
                width=1,
            )

        cursor_rect = pygame.Rect(
            round(origin_x + self.cursor_x * cell_size),
            round(origin_y + self.cursor_y * cell_size),
            max(1, round(cell_size)),
            max(1, round(cell_size)),
        )
        pygame.draw.rect(screen, self.cursor_color, cursor_rect, width=3)

    def _draw_debug_panel(
        self,
        screen: pygame.Surface,
        selected_world_hex: tuple[int, int] | None,
    ) -> None:
        panel_rect = pygame.Rect(self.map_width, 0, self.panel_width, self.map_height)
        pygame.draw.rect(screen, self.panel_bg, panel_rect)

        selected_text = f"{selected_world_hex}" if selected_world_hex is not None else "(none)"
        lines = [
            "Mode: Local",
            f"cursor_x: {self.cursor_x}",
            f"cursor_y: {self.cursor_y}",
            f"grid_w: {self.grid_w}",
            f"grid_h: {self.grid_h}",
            f"Local for selected world hex: {selected_text}",
            "",
            "Controls:",
            "TAB: toggle mode",
            "WASD: move cursor",
            "ESC: quit",
        ]

        y = 18
        for line in lines:
            text_surface = self.font.render(line, True, self.panel_text)
            screen.blit(text_surface, (self.map_width + 14, y))
            y += 24
