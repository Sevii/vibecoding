# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pygame",
# ]
# ///
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with Walls")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Clock
clock = pygame.time.Clock()
FPS = 10

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Helper functions
def draw_cell(position, color):
    x, y = position
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)

def random_position(exclude):
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in exclude:
            return pos

# Snake setup
snake = [(5, 5)]
direction = RIGHT

# Food
food = random_position(snake)

# Walls
wall_count = (GRID_WIDTH * GRID_HEIGHT) // 15  # Sparse walls
walls = []
while len(walls) < wall_count:
    pos = random_position(snake + walls + [food])
    walls.append(pos)

# Game loop
def game_loop():
    global direction, food
    running = True
    grow = False

    while running:
        clock.tick(FPS)
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT

        # Move snake
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        # Collision checks
        if (
            new_head in snake or
            new_head in walls or
            new_head[0] < 0 or new_head[1] < 0 or
            new_head[0] >= GRID_WIDTH or new_head[1] >= GRID_HEIGHT
        ):
            print("Game Over!")
            running = False
            break

        snake.insert(0, new_head)

        if new_head == food:
            food = random_position(snake + walls)
        else:
            snake.pop()

        # Drawing
        draw_cell(food, RED)
        for segment in snake:
            draw_cell(segment, GREEN)
        for wall in walls:
            draw_cell(wall, GRAY)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

# Run game
if __name__ == "__main__":
    game_loop()
