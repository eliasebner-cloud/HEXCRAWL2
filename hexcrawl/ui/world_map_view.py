"""World-map viewport rendering with pan, zoom, hover and selection."""

from __future__ import annotations

import math
from enum import Enum

import pygame

from hexcrawl.core.hex_math import axial_distance, axial_round, axial_to_pixel, pixel_to_axial
from hexcrawl.core.player import Player
from hexcrawl.sim.time_model import TimeModel
from hexcrawl.world.climate import BiomeType, ClimateGen, ClimateTile
from hexcrawl.world.world_config import WorldConfig
from hexcrawl.world.worldgen import TerrainType, WorldGen


class ColorMode(str, Enum):
    TERRAIN = "TERRAIN"
    BIOME = "BIOME"


class WorldMapView:
    """Renders a viewport-only pointy-top axial hex grid."""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        time_model: TimeModel,
        player: Player,
        world_gen: WorldGen,
        climate_gen: ClimateGen,
        world_config: WorldConfig,
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
        self.climate_gen = climate_gen
        self.world_config = world_config
        self.color_mode = ColorMode.TERRAIN
        self.debug_verbosity = "STD"
        self.show_rivers = False
        self.river_threshold = 250
        self.river_threshold_step = 25

        self.terrain_colors: dict[TerrainType, tuple[int, int, int]] = {
            TerrainType.OCEAN: (45, 89, 134),
            TerrainType.COAST: (208, 188, 132),
            TerrainType.PLAINS: (108, 153, 89),
            TerrainType.HILLS: (114, 122, 90),
            TerrainType.MOUNTAINS: (126, 132, 142),
            TerrainType.SNOW: (228, 235, 245),
        }

        self.biome_colors: dict[BiomeType, tuple[int, int, int]] = {
            BiomeType.OCEAN: (45, 89, 134),
            BiomeType.COASTAL: (210, 196, 146),
            BiomeType.DESERT: (232, 204, 120),
            BiomeType.SAVANNA: (170, 168, 94),
            BiomeType.GRASSLAND: (104, 156, 90),
            BiomeType.TEMPERATE_FOREST: (68, 122, 74),
            BiomeType.TAIGA: (88, 118, 114),
            BiomeType.TUNDRA: (164, 174, 166),
            BiomeType.ALPINE: (205, 211, 222),
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

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.show_rivers = not self.show_rivers

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFTBRACKET:
            self.river_threshold = max(1, self.river_threshold - self.river_threshold_step)

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHTBRACKET:
            self.river_threshold += self.river_threshold_step

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            self.color_mode = (
                ColorMode.BIOME if self.color_mode == ColorMode.TERRAIN else ColorMode.TERRAIN
            )

    def set_debug_verbosity(self, verbosity: str) -> None:
        if verbosity not in {"MIN", "STD", "ADV"}:
            raise ValueError(f"Unsupported debug verbosity: {verbosity}")
        self.debug_verbosity = verbosity

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

    def _tile_color(self, q: int, r: int) -> tuple[int, int, int]:
        tile = self.world_gen.get_tile(q, r)
        if self.color_mode == ColorMode.TERRAIN:
            return self.terrain_colors[tile.terrain_type]
        climate = self.climate_gen.get_tile(q, r, tile.terrain_type, tile.height)
        return self.biome_colors[climate.biome_type]

    def _climate_for_hex(self, hex_coords: tuple[int, int] | None) -> ClimateTile | None:
        if hex_coords is None:
            return None
        q, r = hex_coords
        tile = self.world_gen.get_tile(q, r)
        return self.climate_gen.get_tile(q, r, tile.terrain_type, tile.height)

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
        visible_hexes: list[tuple[int, int, float, float]] = []

        for q in range(q_min, q_max + 1):
            for r in range(r_min, r_max + 1):
                wx, wy = axial_to_pixel(q, r, self.hex_size)
                sx, sy = self._world_to_screen(wx, wy)
                points = self._hex_corners(sx, sy)

                if not self.world_config.is_r_in_bounds(r):
                    continue

                fill_color = self._tile_color(q, r)
                pygame.draw.polygon(screen, fill_color, points, width=0)
                pygame.draw.polygon(screen, self.grid_line_color, points, width=1)
                visible_hexes.append((q, r, sx, sy))

        self._draw_river_overlay(screen, visible_hexes)

        for q, r, sx, sy in visible_hexes:
            points = self._hex_corners(sx, sy)
            if self.hover_hex is not None and (q, r) == self.hover_hex:
                pygame.draw.polygon(screen, self.hover_color, points, width=3)

            if self.selected_hex is not None and (q, r) == self.selected_hex:
                pygame.draw.polygon(screen, self.selected_color, points, width=4)

            if (q, r) == (player_q, player_r):
                pygame.draw.polygon(screen, self.player_color, points, width=6)

    def _draw_river_overlay(
        self,
        screen: pygame.Surface,
        visible_hexes: list[tuple[int, int, float, float]],
    ) -> None:
        if not self.show_rivers:
            return

        river_color = (52, 152, 219)
        lake_color = (86, 178, 255)

        for q, r, sx, sy in visible_hexes:
            strength = self.world_gen.get_river_strength(q, r)
            if strength < self.river_threshold:
                if self.world_gen.is_lake(q, r):
                    pygame.draw.circle(screen, lake_color, (int(sx), int(sy)), max(2, int(self.hex_size * 0.20)))
                continue

            flow_to = self.world_gen.get_flow_to(q, r)
            if flow_to is None:
                continue

            downstream_q, downstream_r = flow_to
            downstream_strength = self.world_gen.get_river_strength(downstream_q, downstream_r)
            downstream_tile = self.world_gen.get_tile(downstream_q, downstream_r)
            if (
                downstream_strength < self.river_threshold
                and downstream_tile.terrain_type != TerrainType.OCEAN
            ):
                continue

            if self.world_config.wrap_x:
                world_width = self.world_config.width
                wraps = round((q - downstream_q) / world_width)
                downstream_q = downstream_q + wraps * world_width

            nx, ny = axial_to_pixel(downstream_q, downstream_r, self.hex_size)
            nsx, nsy = self._world_to_screen(nx, ny)
            width = max(1, int(min(4, 1 + math.log2(max(1, strength)) / 2)))
            pygame.draw.line(screen, river_color, (sx, sy), (nsx, nsy), width=width)

    def _draw_debug_panel(self, screen: pygame.Surface) -> None:
        panel_rect = pygame.Rect(self.world_width, 0, self.panel_width, self.world_height)
        pygame.draw.rect(screen, self.panel_bg, panel_rect)

        travel_cost = self.selected_travel_cost

        hover_tile = None if self.hover_hex is None else self.world_gen.get_tile(*self.hover_hex)
        selected_tile = None if self.selected_hex is None else self.world_gen.get_tile(*self.selected_hex)
        hover_climate = self._climate_for_hex(self.hover_hex)
        selected_climate = self._climate_for_hex(self.selected_hex)

        lines = [
            "Mode: WORLD",
            f"Debug verbosity: {self.debug_verbosity}",
            f"World profile: {self.world_config.profile.value}",
            f"World size: {self.world_config.width}x{self.world_config.height}",
            f"Seed: {self.world_gen.seed}",
            f"Climate seed: {self.climate_gen.seed}",
            f"Rivers: {'ON' if self.show_rivers else 'OFF'}",
            f"River threshold: {self.river_threshold}",
            f"Player hex:   {self.player.hex_pos}",
            f"Selected hex: {self.selected_hex if self.selected_hex is not None else '(none)'}",
            f"Hover hex:    {self.hover_hex if self.hover_hex is not None else '(none)'}",
        ]

        if self.debug_verbosity in {"STD", "ADV"}:
            lines.extend(
                [
                    f"Color mode: {self.color_mode.value}",
                    (
                        "Hover terrain: "
                        f"{hover_tile.terrain_type.value if hover_tile is not None else '(none)'}"
                    ),
                    (
                        "Hover height:  "
                        f"{hover_tile.height:.3f}" if hover_tile is not None else "Hover height:  (none)"
                    ),
                    (
                        "Hover biome:   "
                        f"{hover_climate.biome_type.value if hover_climate is not None else '(none)'}"
                    ),
                    (
                        "Hover heat/moisture: "
                        f"{hover_climate.heat:.3f}/{hover_climate.moisture:.3f}"
                        if hover_climate is not None
                        else "Hover heat/moisture: (none)"
                    ),
                    (
                        "Selected terrain: "
                        f"{selected_tile.terrain_type.value if selected_tile is not None else '(none)'}"
                    ),
                    (
                        "Selected height:  "
                        f"{selected_tile.height:.3f}"
                        if selected_tile is not None
                        else "Selected height:  (none)"
                    ),
                    (
                        "Selected biome:   "
                        f"{selected_climate.biome_type.value if selected_climate is not None else '(none)'}"
                    ),
                    (
                        "Selected heat/moisture: "
                        f"{selected_climate.heat:.3f}/{selected_climate.moisture:.3f}"
                        if selected_climate is not None
                        else "Selected heat/moisture: (none)"
                    ),
                    (
                        "Travel cost:  "
                        f"{travel_cost if travel_cost is not None else '(none)'}"
                    ),
                    f"Wrap X: {self.world_config.wrap_x}",
                    f"Zoom: {self.zoom:.2f}",
                    (
                        "Camera offset: "
                        f"({self.camera_offset_x:.1f}, {self.camera_offset_y:.1f})"
                    ),
                    f"Mouse pixel:  {self.mouse_pixel}",
                    f"Local time: {self.time_model.local_elapsed_mmss}",
                    f"World ticks: {self.time_model.world_tick_count}",
                ]
            )

        if self.debug_verbosity == "ADV":
            lines.extend(
                [
                    (
                        "Hover river/lake/flow: "
                        f"{self.world_gen.get_river_strength(*self.hover_hex)}/"
                        f"{'lake' if self.world_gen.is_lake(*self.hover_hex) else '-'}/"
                        f"{self.world_gen.get_flow_to(*self.hover_hex)}"
                        if self.hover_hex is not None
                        else "Hover river/lake/flow: (none)"
                    ),
                    (
                        "Selected river/lake/flow: "
                        f"{self.world_gen.get_river_strength(*self.selected_hex)}/"
                        f"{'lake' if self.world_gen.is_lake(*self.selected_hex) else '-'}/"
                        f"{self.world_gen.get_flow_to(*self.selected_hex)}"
                        if self.selected_hex is not None
                        else "Selected river/lake/flow: (none)"
                    ),
                    f"World tile cache: {len(self.world_gen._tile_cache)}/{self.world_gen._tile_cache_maxsize}",
                    f"World height cache: {len(self.world_gen._height_cache)}/{self.world_gen._height_cache_maxsize}",
                    f"World raw-height cache: {len(self.world_gen._raw_height_cache)}/{self.world_gen._raw_height_cache_maxsize}",
                    (
                        "World boundary cache: "
                        f"{len(self.world_gen._boundary_influence_cache)}/{self.world_gen._boundary_influence_cache_maxsize}"
                    ),
                    f"Climate cache: {len(self.climate_gen._climate_cache)}/{self.climate_gen._cache_maxsize}",
                    (
                        "Tectonics plate cache: "
                        f"{len(self.world_gen._tectonics._plate_cache)}/{self.world_gen._tectonics._cache_maxsize}"
                    ),
                    (
                        "Tectonics boundary cache: "
                        f"{len(self.world_gen._tectonics._boundary_cache)}/{self.world_gen._tectonics._cache_maxsize}"
                    ),
                ]
            )

        lines.extend(
            [
                "",
                "Controls:",
                "TAB: toggle mode",
                "F2: debug verbosity",
                "LMB: select hex",
                "ENTER/G: travel to selected",
                "B: toggle biome view",
                "R: toggle rivers",
                "[/]: river threshold -/+",
                "RMB drag: pan",
                "Wheel: zoom",
                "F11: toggle fullscreen",
                "T: world step",
                "ESC: quit",
            ]
        )

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
