"""HEXCRAWL bootstrap entry point."""

from __future__ import annotations

import pygame

from hexcrawl.core.player import Player
from hexcrawl.sim.time_model import TimeModel
from hexcrawl.ui.local_map_view import LocalMapView
from hexcrawl.ui.world_map_view import WorldMapView

WINDOW_TITLE = "HEXCRAWL"
WINDOW_SIZE = (1280, 720)
TARGET_FPS = 60


def run() -> None:
    """Start the world-map skeleton with pan/zoom/select interactions."""
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption(WINDOW_TITLE)

    clock = pygame.time.Clock()
    time_model = TimeModel()
    player = Player()
    world_map = WorldMapView(WINDOW_SIZE[0], WINDOW_SIZE[1], time_model, player)
    local_map = LocalMapView(WINDOW_SIZE[0], WINDOW_SIZE[1], time_model, player)
    mode = "WORLD"

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
