"""World-map viewport rendering with pan, zoom, hover and selection."""

from __future__ import annotations

import math

import pygame

from hexcrawl.core.hex_math import axial_distance, axial_round, axial_to_pixel, pixel_to_axial
from hexcrawl.core.player import Player
from hexcrawl.sim.time_model import TimeModel
from hexcrawl.world.worldgen import TerrainType, WorldGen


class WorldMapView:
    """Renders a viewport-only pointy-top axial hex grid."""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        time_model: TimeModel,
        player: Player,
        world_gen: WorldGen,
    ) -> None:
        self.panel_width = 280
        self.world_width = max(200, screen_width - self.panel_width)
        self.world_height = screen_height

        self.base_hex_size = 28.0
        self.zoom = 1.0
        self.zoom_min = 0.4
        self.zoom_max = 2.5

        self.camera_offset_x = self.world_width / 2.0
        self.camera_offset_y = self.world_height / 2.0

        self.dragging = False
        self.last_mouse_pos: tuple[int, int] | None = None

        self.hover_hex: tuple[int, int] | None = None
        self.selected_hex: tuple[int, int] | None = None
        self.mouse_pixel = (0, 0)

        self.background_color = (16, 18, 22)
        self.grid_line_color = (76, 86, 102)
        self.hover_color = (97, 175, 239)
        self.selected_color = (224, 108, 117)
        self.player_color = (152, 195, 121)
        self.panel_bg = (28, 32, 40)
        self.panel_text = (225, 230, 240)

        self.font = pygame.font.SysFont("consolas", 18)
        self.time_model = time_model
        self.player = player
        self.world_gen = world_gen

        self.terrain_colors: dict[TerrainType, tuple[int, int, int]] = {
            TerrainType.OCEAN: (45, 89, 134),
            TerrainType.COAST: (208, 188, 132),
            TerrainType.PLAINS: (108, 153, 89),
            TerrainType.HILLS: (114, 122, 90),
            TerrainType.MOUNTAINS: (126, 132, 142),
            TerrainType.SNOW: (228, 235, 245),
        }

    @property
    def hex_size(self) -> float:
        return self.base_hex_size * self.zoom

    @property
    def selected_travel_cost(self) -> int | None:
        if self.selected_hex is None:
            return None
        return axial_distance(self.player.hex_pos, self.selected_hex)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                self.dragging = True
                self.last_mouse_pos = event.pos
            elif event.button == 1 and self._mouse_in_world(event.pos):
                self.selected_hex = self._screen_to_axial(event.pos[0], event.pos[1])
            elif event.button == 4:
                self._apply_zoom(1.1, event.pos)
            elif event.button == 5:
                self._apply_zoom(1.0 / 1.1, event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self.dragging = False
            self.last_mouse_pos = None

        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pixel = event.pos
            if self.dragging and self.last_mouse_pos is not None:
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                self.camera_offset_x += dx
                self.camera_offset_y += dy
                self.last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self._apply_zoom(1.1, pygame.mouse.get_pos())
            elif event.y < 0:
                self._apply_zoom(1.0 / 1.1, pygame.mouse.get_pos())

        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_g):
            self.travel_to_selected()

    def travel_to_selected(self) -> None:
        """Move player to selected hex and spend world ticks based on distance."""
        if self.selected_hex is None:
            return

        distance = axial_distance(self.player.hex_pos, self.selected_hex)
        if distance <= 0:
            return

        self.player.move_to(*self.selected_hex)
        self.time_model.world_step(distance)

    def update(self, dt: float) -> None:
        del dt
        mx, my = pygame.mouse.get_pos()
        self.mouse_pixel = (mx, my)
        if self._mouse_in_world((mx, my)):
            self.hover_hex = self._screen_to_axial(mx, my)
        else:
            self.hover_hex = None

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(self.background_color)
        self._draw_hex_grid(screen)
        self._draw_debug_panel(screen)

    def _mouse_in_world(self, pos: tuple[int, int]) -> bool:
        return 0 <= pos[0] < self.world_width and 0 <= pos[1] < self.world_height

    def _screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        return sx - self.camera_offset_x, sy - self.camera_offset_y

    def _world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        return wx + self.camera_offset_x, wy + self.camera_offset_y

    def _screen_to_axial(self, sx: float, sy: float) -> tuple[int, int]:
        wx, wy = self._screen_to_world(sx, sy)
        fq, fr = pixel_to_axial(wx, wy, self.hex_size)
        return axial_round(fq, fr)

    def _hex_corners(self, center_x: float, center_y: float) -> list[tuple[float, float]]:
        points: list[tuple[float, float]] = []
        # Pointy-top orientation: corner angle starts at -30 degrees.
        for i in range(6):
            angle = math.radians(60 * i - 30)
            x = center_x + self.hex_size * math.cos(angle)
            y = center_y + self.hex_size * math.sin(angle)
            points.append((x, y))
        return points

    def _draw_hex_grid(self, screen: pygame.Surface) -> None:
        margin = self.hex_size
        corners = [
            self._screen_to_world(-margin, -margin),
            self._screen_to_world(self.world_width + margin, -margin),
            self._screen_to_world(self.world_width + margin, self.world_height + margin),
            self._screen_to_world(-margin, self.world_height + margin),
        ]
        qs: list[float] = []
        rs: list[float] = []
        for wx, wy in corners:
            q, r = pixel_to_axial(wx, wy, self.hex_size)
            qs.append(q)
            rs.append(r)

        q_min = math.floor(min(qs)) - 2
        q_max = math.ceil(max(qs)) + 2
        r_min = math.floor(min(rs)) - 2
        r_max = math.ceil(max(rs)) + 2

        player_q, player_r = self.player.hex_pos

        for q in range(q_min, q_max + 1):
            for r in range(r_min, r_max + 1):
                wx, wy = axial_to_pixel(q, r, self.hex_size)
                sx, sy = self._world_to_screen(wx, wy)
                points = self._hex_corners(sx, sy)

                tile = self.world_gen.get_tile(q, r)
                terrain_color = self.terrain_colors[tile.terrain_type]
                pygame.draw.polygon(screen, terrain_color, points, width=0)
                pygame.draw.polygon(screen, self.grid_line_color, points, width=1)

                if self.hover_hex is not None and (q, r) == self.hover_hex:
                    pygame.draw.polygon(screen, self.hover_color, points, width=3)

                if self.selected_hex is not None and (q, r) == self.selected_hex:
                    pygame.draw.polygon(screen, self.selected_color, points, width=4)

                if (q, r) == (player_q, player_r):
                    pygame.draw.polygon(screen, self.player_color, points, width=6)

    def _draw_debug_panel(self, screen: pygame.Surface) -> None:
        panel_rect = pygame.Rect(self.world_width, 0, self.panel_width, self.world_height)
        pygame.draw.rect(screen, self.panel_bg, panel_rect)

        travel_cost = self.selected_travel_cost

        hover_tile = None if self.hover_hex is None else self.world_gen.get_tile(*self.hover_hex)
        selected_tile = None if self.selected_hex is None else self.world_gen.get_tile(*self.selected_hex)

        lines = [
            "Mode: World",
            f"Player hex:   {self.player.hex_pos}",
            f"Selected hex: {self.selected_hex if self.selected_hex is not None else '(none)'}",
            f"Hover hex:    {self.hover_hex if self.hover_hex is not None else '(none)'}",
            (
                "Hover terrain: "
                f"{hover_tile.terrain_type.value if hover_tile is not None else '(none)'}"
            ),
            (
                "Hover height:  "
                f"{hover_tile.height:.3f}" if hover_tile is not None else "Hover height:  (none)"
            ),
            (
                "Selected terrain: "
                f"{selected_tile.terrain_type.value if selected_tile is not None else '(none)'}"
            ),
            (
                "Selected height:  "
                f"{selected_tile.height:.3f}" if selected_tile is not None else "Selected height:  (none)"
            ),
            (
                "Travel cost:  "
                f"{travel_cost if travel_cost is not None else '(none)'}"
            ),
            f"Seed: {self.world_gen.seed}",
            f"Mouse pixel:  {self.mouse_pixel}",
            (
                "Camera offset: "
                f"({self.camera_offset_x:.1f}, {self.camera_offset_y:.1f})"
            ),
            f"Zoom: {self.zoom:.2f}",
            f"Local time: {self.time_model.local_elapsed_mmss}",
            f"World ticks: {self.time_model.world_tick_count}",
            "",
            "Controls:",
            "TAB: toggle mode",
            "LMB: select hex",
            "ENTER/G: travel to selected",
            "RMB drag: pan",
            "Wheel: zoom",
            "T: world step",
            "ESC: quit",
        ]

        y = 18
        for line in lines:
            text_surface = self.font.render(line, True, self.panel_text)
            screen.blit(text_surface, (self.world_width + 14, y))
            y += 24

    def _apply_zoom(self, factor: float, pivot_screen: tuple[int, int]) -> None:
        old_zoom = self.zoom
        new_zoom = max(self.zoom_min, min(self.zoom_max, old_zoom * factor))
        if abs(new_zoom - old_zoom) < 1e-8:
            return

        px, py = pivot_screen
        if not self._mouse_in_world((int(px), int(py))):
            px = self.world_width / 2.0
            py = self.world_height / 2.0

        world_before_x = px - self.camera_offset_x
        world_before_y = py - self.camera_offset_y

        scale = new_zoom / old_zoom
        self.camera_offset_x = px - (world_before_x * scale)
        self.camera_offset_y = py - (world_before_y * scale)
        self.zoom = new_zoom
