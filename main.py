"""HEXCRAWL bootstrap entry point."""

import pygame


WINDOW_TITLE = "HEXCRAWL"
WINDOW_SIZE = (960, 540)
BACKGROUND_COLOR = (20, 22, 26)


def run() -> None:
    """Start a minimal pygame-ce application loop."""
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

    frame = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        fps = clock.get_fps()
        pygame.display.set_caption(f"{WINDOW_TITLE} | Press ESC to quit | FPS: {fps:05.1f}")

        screen.fill(BACKGROUND_COLOR)
        pygame.display.flip()

        clock.tick(60)
        frame += 1

    pygame.quit()


if __name__ == "__main__":
    run()
