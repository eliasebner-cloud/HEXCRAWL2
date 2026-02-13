"""HEXCRAWL bootstrap entry point."""

from __future__ import annotations

import pygame

from hexcrawl.core.player import Player
from hexcrawl.sim.time_model import TimeModel
from hexcrawl.ui.local_map_view import LocalMapView
from hexcrawl.ui.world_map_view import WorldMapView
from hexcrawl.world.climate import ClimateGen
from hexcrawl.world.world_config import WorldProfile, build_world_config
from hexcrawl.world.worldgen import WorldGen

WINDOW_TITLE = "HEXCRAWL"
WINDOW_SIZE = (1920, 1080)
TARGET_FPS = 60
WORLD_SEED = 1337
CLIMATE_SEED = WORLD_SEED + 1
WORLD_PROFILE = WorldProfile.DEV
DEBUG_VERBOSITY_CYCLE = ("MIN", "STD", "ADV")


def _display_flags(fullscreen: bool) -> int:
    base_flags = pygame.SCALED
    if fullscreen:
        return base_flags | pygame.FULLSCREEN
    return base_flags


def _set_display_mode(fullscreen: bool) -> pygame.Surface:
    return pygame.display.set_mode(WINDOW_SIZE, _display_flags(fullscreen))


def run() -> None:
    """Start the world-map skeleton with pan/zoom/select interactions."""
    pygame.init()
    is_fullscreen = True
    try:
        screen = _set_display_mode(is_fullscreen)
    except pygame.error:
        is_fullscreen = False
        screen = _set_display_mode(is_fullscreen)
    pygame.display.set_caption(WINDOW_TITLE)

    clock = pygame.time.Clock()
    time_model = TimeModel()
    player = Player()
    world_config = build_world_config(WORLD_PROFILE)
    world_gen = WorldGen(WORLD_SEED, world_config)
    climate_gen = ClimateGen(CLIMATE_SEED, world_config)
    world_map = WorldMapView(
        WINDOW_SIZE[0],
        WINDOW_SIZE[1],
        time_model,
        player,
        world_gen,
        climate_gen,
        world_config,
    )
    local_map = LocalMapView(
        WINDOW_SIZE[0],
        WINDOW_SIZE[1],
        time_model,
        player,
        world_config,
        WORLD_SEED,
        CLIMATE_SEED,
    )
    mode = "WORLD"
    debug_verbosity = "STD"
    world_map.set_debug_verbosity(debug_verbosity)
    local_map.set_debug_verbosity(debug_verbosity)

    running = True
    while running:
        dt = clock.tick(TARGET_FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                mode = "LOCAL" if mode == "WORLD" else "WORLD"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
                try:
                    screen = _set_display_mode(is_fullscreen)
                except pygame.error:
                    is_fullscreen = False
                    screen = _set_display_mode(is_fullscreen)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                level_index = DEBUG_VERBOSITY_CYCLE.index(debug_verbosity)
                debug_verbosity = DEBUG_VERBOSITY_CYCLE[(level_index + 1) % len(DEBUG_VERBOSITY_CYCLE)]
                world_map.set_debug_verbosity(debug_verbosity)
                local_map.set_debug_verbosity(debug_verbosity)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                time_model.world_step()
            else:
                if mode == "WORLD":
                    world_map.handle_event(event)
                else:
                    local_map.handle_event(event)

        time_model.update(dt)

        if mode == "WORLD":
            world_map.update(dt)
            world_map.draw(screen)
        else:
            local_map.update(dt)
            local_context_hex = player.hex_pos
            local_map.draw(screen, local_context_hex)

        fps = clock.get_fps()
        pygame.display.set_caption(f"{WINDOW_TITLE} | FPS: {fps:05.1f}")
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()
