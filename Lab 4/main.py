import pygame
from game.game_engine import GameEngine

# Initialize pygame/Start application
# Use a known sample format so the generated sound effects work consistently.
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Pygame Version")

# Colors
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Game loop
engine = GameEngine(WIDTH, HEIGHT)

def main():
    running = True
    while running:
        SCREEN.fill(SKY_BLUE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            engine.handle_event(event)

        if engine.should_exit:
            running = False

        engine.handle_input()
        engine.update()
        engine.render(SCREEN)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
