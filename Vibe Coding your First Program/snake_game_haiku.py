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

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Game settings
GAME_SPEED = 10  # Frames per second

class SnakeGame:
    def __init__(self):
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        
        # Snake initial setup
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # Initial direction: right
        
        # Game state
        self.score = 0
        self.game_over = False

        # Initialize walls first
        self.walls = self.generate_walls()
        
        # Then generate food
        self.food = self.generate_food()

    def generate_food(self):
        """Generate food at a random unoccupied location"""
        attempts = 0
        max_attempts = 100
        while attempts < max_attempts:
            food_pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            # Ensure food is not on snake or walls
            if (food_pos not in self.snake and 
                food_pos not in self.walls):
                return food_pos
            attempts += 1
        
        # Fallback if no suitable position found
        return (GRID_WIDTH // 2, GRID_HEIGHT // 2)

    def generate_walls(self):
        """Generate a set of walls randomly distributed"""
        walls = set()
        # Add some boundary walls
        for x in range(GRID_WIDTH):
            walls.add((x, 0))
            walls.add((x, GRID_HEIGHT - 1))
        for y in range(GRID_HEIGHT):
            walls.add((0, y))
            walls.add((GRID_WIDTH - 1, y))
        
        # Add some random internal walls
        num_walls = random.randint(10, 30)
        while len(walls) < num_walls:
            wall_pos = (
                random.randint(1, GRID_WIDTH - 2),
                random.randint(1, GRID_HEIGHT - 2)
            )
            if wall_pos not in self.snake:
                walls.add(wall_pos)
        
        return walls

    def move_snake(self):
        """Move the snake and handle growth and collisions"""
        head = (
            self.snake[0][0] + self.direction[0],
            self.snake[0][1] + self.direction[1]
        )
        
        # Check wall collision
        if (head in self.walls or 
            head[0] < 0 or head[0] >= GRID_WIDTH or 
            head[1] < 0 or head[1] >= GRID_HEIGHT or 
            head in self.snake[1:]):
            self.game_over = True
            return
        
        # Add new head
        self.snake.insert(0, head)
        
        # Check food collision
        if head == self.food:
            self.score += 1
            self.food = self.generate_food()
        else:
            # Remove tail if not eating
            self.snake.pop()

    def draw(self):
        """Draw all game elements"""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(
                self.screen, 
                GRAY, 
                (wall[0]*GRID_SIZE, wall[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
            )
        
        # Draw snake
        for segment in self.snake:
            pygame.draw.rect(
                self.screen, 
                GREEN, 
                (segment[0]*GRID_SIZE, segment[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
            )
        
        # Draw food
        pygame.draw.rect(
            self.screen, 
            RED, 
            (self.food[0]*GRID_SIZE, self.food[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
        )
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Update display
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while not self.game_over:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Handle keyboard input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.direction = (1, 0)
            
            # Move snake
            self.move_snake()
            
            # Draw game state
            self.draw()
            
            # Control game speed
            self.clock.tick(GAME_SPEED)
        
        # Game over screen
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        game_over_text = font.render('GAME OVER', True, RED)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        pygame.display.flip()
        
        # Wait before closing
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

def main():
    """Start the game"""
    game = SnakeGame()
    game.run()

if __name__ == '__main__':
    main()