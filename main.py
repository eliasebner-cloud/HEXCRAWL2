"""HEXCRAWL bootstrap entry point."""

from __future__ import annotations

import pygame

from hexcrawl.ui.local_map_view import LocalMapView
from hexcrawl.ui.world_map_view import WorldMapView

WINDOW_TITLE = "HEXCRAWL"
WINDOW_SIZE = (1280, 720)
TARGET_FPS = 60


MODE_WORLD = "world"
MODE_LOCAL = "local"


def run() -> None:
    """Start the WORLD/LOCAL skeleton with mode toggle."""
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption(WINDOW_TITLE)

    clock = pygame.time.Clock()
    world_map = WorldMapView(WINDOW_SIZE[0], WINDOW_SIZE[1])
    local_map = LocalMapView(WINDOW_SIZE[0], WINDOW_SIZE[1])
    mode = MODE_WORLD

    running = True
    while running:
        dt = clock.tick(TARGET_FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                mode = MODE_LOCAL if mode == MODE_WORLD else MODE_WORLD
                if mode == MODE_LOCAL:
                    local_map.ensure_initialized()
            elif mode == MODE_WORLD:
                world_map.handle_event(event)
            else:
                local_map.handle_event(event)

        if mode == MODE_WORLD:
            world_map.update(dt)
            world_map.draw(screen)
        else:
            local_map.update(dt)
            local_map.draw(screen, world_map.selected_hex)

        fps = clock.get_fps()
        mode_label = "WORLD" if mode == MODE_WORLD else "LOCAL"
        pygame.display.set_caption(f"{WINDOW_TITLE} [{mode_label}] | FPS: {fps:05.1f}")
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()
