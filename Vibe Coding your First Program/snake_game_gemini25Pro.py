# /// script
# requires-python = ">=3.12"
# dependencies = [
#  "pygame",
# ]
# ///

import pygame
import random
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255) # For walls
YELLOW = (255, 255, 0) # For food

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

FPS = 10

# --- Helper Functions ---
def draw_grid(surface):
    """Draws the grid lines on the surface (optional, for debugging or style)."""
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, WHITE, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, WHITE, (0, y), (SCREEN_WIDTH, y))

def draw_object(surface, color, pos):
    """Draws a single grid-based object."""
    rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, BLACK, rect, 1) # Border

def get_random_empty_position(snake_body, walls):
    """Finds a random empty position not occupied by the snake or walls."""
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake_body and pos not in walls:
            return pos

def generate_walls(num_walls, snake_start_pos):
    """Generates a list of wall positions, ensuring they are not too dense."""
    walls = []
    occupied_for_walls = {snake_start_pos} # Snake start shouldn't be a wall

    # Define potential wall cluster starting points
    # Ensure walls are not too close to the edges initially for easier start
    min_dist_from_edge = 3

    for _ in range(num_walls):
        attempts = 0
        while attempts < 50: # Try to find a good spot
            start_x = random.randint(min_dist_from_edge, GRID_WIDTH - 1 - min_dist_from_edge)
            start_y = random.randint(min_dist_from_edge, GRID_HEIGHT - 1 - min_dist_from_edge)
            wall_pos = (start_x, start_y)

            # Check if it's too close to existing walls or snake start
            too_close = False
            if wall_pos in occupied_for_walls:
                too_close = True
            else:
                for ow_x, ow_y in occupied_for_walls:
                    if abs(wall_pos[0] - ow_x) <= 1 and abs(wall_pos[1] - ow_y) <= 1:
                        too_close = True
                        break
            
            if not too_close:
                walls.append(wall_pos)
                occupied_for_walls.add(wall_pos)
                # Optionally, add a few connected wall segments for small clusters
                for _ in range(random.randint(0,2)): # Add 0 to 2 more segments nearby
                    dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
                    next_wall_x, next_wall_y = wall_pos[0] + dx, wall_pos[1] + dy
                    if 0 <= next_wall_x < GRID_WIDTH and 0 <= next_wall_y < GRID_HEIGHT:
                        next_wall_pos = (next_wall_x, next_wall_y)
                        if next_wall_pos not in occupied_for_walls:
                            walls.append(next_wall_pos)
                            occupied_for_walls.add(next_wall_pos)
                break
            attempts += 1
    return list(set(walls)) # Remove duplicates

# --- Game Class ---
class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake Game")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 35)
        self.running = True
        self.game_over_flag = False
        self.reset_game()

    def reset_game(self):
        """Resets the game state for a new game."""
        self.snake = Snake()
        self.walls = generate_walls(num_walls=20, snake_start_pos=self.snake.body[0]) # Adjust num_walls as needed
        self.food = Food(self.snake.body, self.walls)
        self.score = 0
        self.game_over_flag = False
        self.paused = False

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            if not self.game_over_flag and not self.paused:
                self.update()
            self.render()
            self.clock.tick(FPS + len(self.snake.body) // 3) # Speed up slightly as snake grows

        pygame.quit()
        sys.exit()

    def handle_input(self):
        """Handles user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.game_over_flag:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        self.running = False
                else:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    if not self.paused:
                        if event.key == pygame.K_UP:
                            self.snake.change_direction(UP)
                        elif event.key == pygame.K_DOWN:
                            self.snake.change_direction(DOWN)
                        elif event.key == pygame.K_LEFT:
                            self.snake.change_direction(LEFT)
                        elif event.key == pygame.K_RIGHT:
                            self.snake.change_direction(RIGHT)

    def update(self):
        """Updates game state."""
        self.snake.move()

        # Check for food collision
        if self.snake.get_head_position() == self.food.position:
            self.snake.grow()
            self.food.spawn_new(self.snake.body, self.walls)
            self.score += 1

        # Check for game over conditions
        # 1. Collision with walls
        if self.snake.get_head_position() in self.walls:
            self.game_over()

        # 2. Collision with screen boundaries
        head_x, head_y = self.snake.get_head_position()
        if not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT):
            self.game_over()

        # 3. Collision with self
        if self.snake.get_head_position() in self.snake.body[1:]:
            self.game_over()

    def render(self):
        """Renders the game to the screen."""
        self.screen.fill(BLACK)
        # draw_grid(self.screen) # Optional: for debugging

        # Draw walls
        for wall_pos in self.walls:
            draw_object(self.screen, BLUE, wall_pos)

        # Draw snake
        self.snake.draw(self.screen)

        # Draw food
        self.food.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        if self.game_over_flag:
            self.show_game_over_screen()
        elif self.paused:
            self.show_pause_screen()

        pygame.display.flip()


    def game_over(self):
        """Sets the game over state."""
        self.game_over_flag = True

    def show_game_over_screen(self):
        """Displays the game over message."""
        game_over_text = self.font.render("GAME OVER!", True, RED)
        prompt_text = self.font.render("Press 'R' to Restart or 'Q' to Quit", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30))
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30))
        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(prompt_text, prompt_rect)

    def show_pause_screen(self):
        """Displays the pause message."""
        pause_text = self.font.render("PAUSED", True, YELLOW)
        prompt_text = self.font.render("Press 'P' to Resume", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20))
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20))
        self.screen.blit(pause_text, text_rect)
        self.screen.blit(prompt_text, prompt_rect)


# --- Snake Class ---
class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)] # Start in the middle
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT]) # Initial random direction
        self.grow_pending = False

    def get_head_position(self):
        return self.body[0]

    def move(self):
        current_head = self.get_head_position()
        new_head = (current_head[0] + self.direction[0], current_head[1] + self.direction[1])

        self.body.insert(0, new_head)

        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

    def grow(self):
        self.grow_pending = True

    def change_direction(self, new_direction):
        # Prevent the snake from reversing directly onto itself
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def draw(self, surface):
        for segment in self.body:
            draw_object(surface, GREEN, segment)
        # Draw eyes on the head for a bit more character
        head_x, head_y = self.get_head_position()
        eye_size = GRID_SIZE // 5
        eye_offset_1 = GRID_SIZE // 4
        eye_offset_2 = GRID_SIZE - GRID_SIZE // 4 - eye_size

        if self.direction == UP:
            eye1_pos = (head_x * GRID_SIZE + eye_offset_1, head_y * GRID_SIZE + eye_offset_1)
            eye2_pos = (head_x * GRID_SIZE + eye_offset_2, head_y * GRID_SIZE + eye_offset_1)
        elif self.direction == DOWN:
            eye1_pos = (head_x * GRID_SIZE + eye_offset_1, head_y * GRID_SIZE + eye_offset_2)
            eye2_pos = (head_x * GRID_SIZE + eye_offset_2, head_y * GRID_SIZE + eye_offset_2)
        elif self.direction == LEFT:
            eye1_pos = (head_x * GRID_SIZE + eye_offset_1, head_y * GRID_SIZE + eye_offset_1)
            eye2_pos = (head_x * GRID_SIZE + eye_offset_1, head_y * GRID_SIZE + eye_offset_2)
        elif self.direction == RIGHT:
            eye1_pos = (head_x * GRID_SIZE + eye_offset_2, head_y * GRID_SIZE + eye_offset_1)
            eye2_pos = (head_x * GRID_SIZE + eye_offset_2, head_y * GRID_SIZE + eye_offset_2)
        
        if self.direction in [UP, DOWN, LEFT, RIGHT]: # Check if direction is valid before drawing eyes
            pygame.draw.rect(surface, BLACK, (eye1_pos[0], eye1_pos[1], eye_size, eye_size))
            pygame.draw.rect(surface, BLACK, (eye2_pos[0], eye2_pos[1], eye_size, eye_size))


# --- Food Class ---
class Food:
    def __init__(self, snake_body, walls):
        self.color = YELLOW
        self.spawn_new(snake_body, walls)

    def spawn_new(self, snake_body, walls):
        self.position = get_random_empty_position(snake_body, walls)

    def draw(self, surface):
        draw_object(surface, self.color, self.position)


# --- Main Execution ---
if __name__ == "__main__":
    game = SnakeGame()
    game.run()