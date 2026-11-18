import pygame
from .bird import Bird
from .pipe import Pipe
from .sound_effects import SoundEffects

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
DIFFICULTIES = {
    "easy": {"label": "Easy", "pipe_speed": 3, "pipe_gap": 190},
    "medium": {"label": "Medium", "pipe_speed": 4, "pipe_gap": 150},
    "hard": {"label": "Hard", "pipe_speed": 6, "pipe_gap": 115},
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.pipe_interval = 90  # frames between pipe spawns
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 52, bold=True)
        self.instruction_font = pygame.font.SysFont("Arial", 22)
        self.sounds = SoundEffects()
        self.should_exit = False
        self.start_new_game("medium")

    def start_new_game(self, difficulty):
        """Reset the game using one of the configured difficulty levels."""
        settings = DIFFICULTIES[difficulty]
        self.difficulty = difficulty
        self.pipe_speed = settings["pipe_speed"]
        self.pipe_gap = settings["pipe_gap"]
        self.bird = Bird(self.width // 4, self.height // 2)
        self._spawn_timer = 0
        self.pipes = [
            Pipe(self.width + 100, self.height, gap=self.pipe_gap, speed=self.pipe_speed)
        ]
        self.score = 0
        self.game_over = False

    def _menu_buttons(self):
        """Return the clickable replay and exit button bounds."""
        button_width = 260
        button_height = 45
        left = (self.width - button_width) // 2
        return {
            "easy": pygame.Rect(left, 355, button_width, button_height),
            "medium": pygame.Rect(left, 410, button_width, button_height),
            "hard": pygame.Rect(left, 465, button_width, button_height),
            "exit": pygame.Rect(left, 535, button_width, button_height),
        }

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                choices = {
                    pygame.K_1: "easy", pygame.K_KP1: "easy", pygame.K_e: "easy",
                    pygame.K_2: "medium", pygame.K_KP2: "medium", pygame.K_m: "medium",
                    pygame.K_3: "hard", pygame.K_KP3: "hard", pygame.K_h: "hard",
                }
                if event.key in choices:
                    self.start_new_game(choices[event.key])
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.should_exit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for choice, button in self._menu_buttons().items():
                    if button.collidepoint(event.pos):
                        if choice == "exit":
                            self.should_exit = True
                        else:
                            self.start_new_game(choice)
                        break
            return

        # Flap is edge-triggered (KEYDOWN / MOUSEBUTTONDOWN), not held.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.bird.flap()
            self.sounds.play("flap")
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bird.flap()
            self.sounds.play("flap")

    def handle_input(self):
        # Reserved for continuously-held-key input; flapping is handled
        # in handle_event instead, so there's nothing to poll here.
        pass

    def _bird_hits_rect(self, rect):
        """Return whether the bird's circular body overlaps ``rect``.

        Checking the nearest point on a pipe to the circle gives a more
        faithful result than testing only the bird's centre (or using its
        square bounding box).
        """
        closest_x = max(rect.left, min(self.bird.x, rect.right))
        closest_y = max(rect.top, min(self.bird.y, rect.bottom))
        dx = self.bird.x - closest_x
        dy = self.bird.y - closest_y
        return dx * dx + dy * dy <= self.bird.radius * self.bird.radius

    def _pipe_collision(self, pipe, previous_x):
        """Check a pipe's whole path for this frame against the bird."""
        # A fast pipe can move past the bird between two frames.  Expand its
        # rectangles over both horizontal positions so that contact anywhere
        # along that movement is still detected.
        left = min(previous_x, pipe.x)
        right = max(previous_x + pipe.width, pipe.x + pipe.width)
        width = right - left
        top = pipe.top_rect()
        bottom = pipe.bottom_rect()
        swept_top = pygame.Rect(left, top.top, width, top.height)
        swept_bottom = pygame.Rect(left, bottom.top, width, bottom.height)
        return self._bird_hits_rect(swept_top) or self._bird_hits_rect(swept_bottom)

    def _end_game(self):
        """End the current round and play the death sound once."""
        if not self.game_over:
            self.game_over = True
            self.sounds.play("die")

    def update(self):
        if self.game_over:
            return

        self.bird.update()

        if self.bird.y - self.bird.radius <= 0 or self.bird.y + self.bird.radius >= self.height:
            self._end_game()
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0
            self.pipes.append(
                Pipe(self.width, self.height, gap=self.pipe_gap, speed=self.pipe_speed)
            )

        for pipe in self.pipes:
            previous_x = pipe.x
            pipe.move()

            if self._pipe_collision(pipe, previous_x):
                self._end_game()
                return

            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1
                self.sounds.play("score")

        self.pipes = [p for p in self.pipes if not p.off_screen()]

    def render(self, screen):
        for pipe in self.pipes:
            pygame.draw.rect(screen, GREEN, pipe.top_rect())
            pygame.draw.rect(screen, GREEN, pipe.bottom_rect())

        pygame.draw.circle(screen, WHITE, (int(self.bird.x), int(self.bird.y)), self.bird.radius)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 165))
            screen.blit(overlay, (0, 0))

            title = self.game_over_font.render("Game Over", True, WHITE)
            final_score = self.font.render(f"Final Score: {self.score}", True, WHITE)
            instruction = self.instruction_font.render("Choose a difficulty to play again", True, WHITE)

            screen.blit(title, title.get_rect(center=(self.width // 2, 220)))
            screen.blit(final_score, final_score.get_rect(center=(self.width // 2, 275)))
            screen.blit(instruction, instruction.get_rect(center=(self.width // 2, 320)))

            button_labels = {
                "easy": "1. Easy  (slower pipes, wider gap)",
                "medium": "2. Medium  (normal)",
                "hard": "3. Hard  (faster pipes, narrower gap)",
                "exit": "Exit  (Esc or Q)",
            }
            for choice, button in self._menu_buttons().items():
                color = (40, 130, 60) if choice != "exit" else (150, 55, 55)
                pygame.draw.rect(screen, color, button, border_radius=8)
                pygame.draw.rect(screen, WHITE, button, width=2, border_radius=8)
                label = self.instruction_font.render(button_labels[choice], True, WHITE)
                screen.blit(label, label.get_rect(center=button.center))
