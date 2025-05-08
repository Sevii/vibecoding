# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pygame",
# ]
# ///

import pygame
import random

# Initialize Pygame
pygame.init()

# Screen Dimensions
WIDTH = 800
HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Create the game screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')

# Clock to control game speed
clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        # Starting position in the middle of the screen
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # Start moving right
        self.grow_to = 0

    def move(self):
        # Get current head position
        head = self.body[0]
        
        # Calculate new head position
        new_head = (
            (head[0] + self.direction[0]) % GRID_WIDTH,
            (head[1] + self.direction[1]) % GRID_HEIGHT
        )
        
        # Check if snake hits itself
        if new_head in self.body:
            return False
        
        # Add new head to the front of the body
        self.body.insert(0, new_head)
        
        # Grow snake if needed
        if self.grow_to > 0:
            self.grow_to -= 1
        else:
            # Remove tail if not growing
            self.body.pop()
        
        return True

    def draw(self):
        for segment in self.body:
            rect = pygame.Rect(
                segment[0] * GRID_SIZE, 
                segment[1] * GRID_SIZE, 
                GRID_SIZE - 1, 
                GRID_SIZE - 1
            )
            pygame.draw.rect(screen, GREEN, rect)

    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

class Food:
    def __init__(self, snake):
        self.position = self.generate_position(snake)

    def generate_position(self, snake):
        while True:
            # Generate random position
            pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            # Ensure food doesn't appear on snake's body
            if pos not in snake.body:
                return pos

    def draw(self):
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE, 
            self.position[1] * GRID_SIZE, 
            GRID_SIZE - 1, 
            GRID_SIZE - 1
        )
        pygame.draw.rect(screen, RED, rect)

def main():
    # Initialize game objects
    snake = Snake()
    food = Food(snake)
    score = 0

    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle key presses for direction
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))

        # Move snake
        if not snake.move():
            # Snake hit itself - game over
            running = False

        # Check if snake ate food
        if snake.body[0] == food.position:
            # Grow snake and generate new food
            snake.grow_to += 1
            score += 1
            food = Food(snake)

        # Clear screen
        screen.fill(BLACK)

        # Draw game objects
        snake.draw()
        food.draw()

        # Update display
        pygame.display.flip()

        # Control game speed
        clock.tick(10)  # 10 frames per second

    # Game over screen
    screen.fill(BLACK)
    font = pygame.font.Font(None, 36)
    text = font.render(f'Game Over! Score: {score}', True, WHITE)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.flip()

    # Wait a moment before closing
    pygame.time.wait(2000)

    # Quit Pygame
    pygame.quit()

# Run the game
if __name__ == '__main__':
    main()
