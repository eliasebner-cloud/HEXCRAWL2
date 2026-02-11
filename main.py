"""HEXCRAWL bootstrap entry point."""

from __future__ import annotations

import pygame

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
    world_map = WorldMapView(WINDOW_SIZE[0], WINDOW_SIZE[1])

    running = True
    while running:
        dt = clock.tick(TARGET_FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                world_map.handle_event(event)

        world_map.update(dt)
        world_map.draw(screen)

        fps = clock.get_fps()
        pygame.display.set_caption(f"{WINDOW_TITLE} | FPS: {fps:05.1f}")
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()
