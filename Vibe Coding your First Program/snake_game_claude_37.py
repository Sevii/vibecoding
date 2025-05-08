# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pygame",
# ]
# ///

import pygame
import random
import sys
from enum import Enum, auto

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class SnakeGame:
    def __init__(self, width=800, height=600, cell_size=20):
        # Initialize pygame
        pygame.init()
        
        # Game settings
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size
        
        # Display settings
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 25)
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GRAY = (128, 128, 128)
        
        # Game state
        self.reset_game()
    
    def reset_game(self):
        # Initialize snake
        self.snake = [(self.grid_width // 2, self.grid_height // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Initialize score
        self.score = 0
        
        # Generate walls
        self.walls = []
        self.generate_walls(wall_count=30)
        
        # Place food
        self.food = None
        self.place_food()
        
        # Game state
        self.game_over = False
    
    def generate_walls(self, wall_count):
        # Clear existing walls
        self.walls = []
        
        # Create border walls
        for x in range(self.grid_width):
            self.walls.append((x, 0))
            self.walls.append((x, self.grid_height - 1))
        
        for y in range(self.grid_height):
            self.walls.append((0, y))
            self.walls.append((self.grid_width - 1, y))
        
        # Create random internal walls
        attempts = 0
        while len(self.walls) < wall_count + (2 * self.grid_width + 2 * self.grid_height - 4) and attempts < 100:
            x = random.randint(2, self.grid_width - 3)
            y = random.randint(2, self.grid_height - 3)
            
            # Avoid placing walls too close to the center (snake start)
            if (abs(x - self.grid_width // 2) < 3 and
                abs(y - self.grid_height // 2) < 3):
                continue
            
            # Avoid placing walls too close to other walls (prevents tight packing)
            if any(abs(wx - x) + abs(wy - y) <= 1 for wx, wy in self.walls if (wx, wy) not in [(0, y), (self.grid_width-1, y), (x, 0), (x, self.grid_height-1)]):
                continue
                
            wall = (x, y)
            if wall not in self.walls:
                self.walls.append(wall)
            
            attempts += 1
    
    def place_food(self):
        # Find all valid positions (not on snake or walls)
        valid_positions = [(x, y) for x in range(1, self.grid_width - 1) 
                          for y in range(1, self.grid_height - 1) 
                          if (x, y) not in self.snake and (x, y) not in self.walls]
        
        if valid_positions:
            self.food = random.choice(valid_positions)
        else:
            # No valid positions, game won
            self.game_over = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if self.game_over and event.key == pygame.K_SPACE:
                    self.reset_game()
                
                # Direction changes
                if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.next_direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.next_direction = Direction.DOWN
                elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.next_direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.next_direction = Direction.RIGHT
    
    def update(self):
        if self.game_over:
            return
        
        # Apply the direction change
        self.direction = self.next_direction
        
        # Move the snake
        head_x, head_y = self.snake[0]
        
        if self.direction == Direction.UP:
            head_y -= 1
        elif self.direction == Direction.DOWN:
            head_y += 1
        elif self.direction == Direction.LEFT:
            head_x -= 1
        elif self.direction == Direction.RIGHT:
            head_x += 1
        
        new_head = (head_x, head_y)
        
        # Check for collisions
        if (new_head in self.snake or 
            new_head in self.walls or 
            head_x < 0 or head_x >= self.grid_width or 
            head_y < 0 or head_y >= self.grid_height):
            self.game_over = True
            return
        
        # Move the snake
        self.snake.insert(0, new_head)
        
        # Check if food is eaten
        if self.food and new_head == self.food:
            self.score += 1
            self.place_food()
        else:
            # Remove the tail if no food eaten
            self.snake.pop()
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            color = self.GREEN if i > 0 else (0, 200, 0)  # Darker green for head
            pygame.draw.rect(self.screen, color, 
                            (x * self.cell_size, y * self.cell_size, 
                             self.cell_size, self.cell_size))
            
            # Add eyes to the head for visual clarity
            if i == 0:
                eye_size = self.cell_size // 5
                eye_offset = self.cell_size // 3
                
                # Position eyes based on direction
                if self.direction == Direction.RIGHT:
                    eye_pos1 = (x * self.cell_size + self.cell_size - eye_offset, y * self.cell_size + eye_offset)
                    eye_pos2 = (x * self.cell_size + self.cell_size - eye_offset, y * self.cell_size + self.cell_size - eye_offset)
                elif self.direction == Direction.LEFT:
                    eye_pos1 = (x * self.cell_size + eye_offset - eye_size, y * self.cell_size + eye_offset)
                    eye_pos2 = (x * self.cell_size + eye_offset - eye_size, y * self.cell_size + self.cell_size - eye_offset)
                elif self.direction == Direction.UP:
                    eye_pos1 = (x * self.cell_size + eye_offset, y * self.cell_size + eye_offset - eye_size)
                    eye_pos2 = (x * self.cell_size + self.cell_size - eye_offset, y * self.cell_size + eye_offset - eye_size)
                else:  # DOWN
                    eye_pos1 = (x * self.cell_size + eye_offset, y * self.cell_size + self.cell_size - eye_offset)
                    eye_pos2 = (x * self.cell_size + self.cell_size - eye_offset, y * self.cell_size + self.cell_size - eye_offset)
                
                pygame.draw.circle(self.screen, self.WHITE, eye_pos1, eye_size)
                pygame.draw.circle(self.screen, self.WHITE, eye_pos2, eye_size)
        
        # Draw food
        if self.food:
            x, y = self.food
            pygame.draw.rect(self.screen, self.RED, 
                            (x * self.cell_size, y * self.cell_size, 
                             self.cell_size, self.cell_size))
        
        # Draw walls
        for x, y in self.walls:
            pygame.draw.rect(self.screen, self.GRAY, 
                            (x * self.cell_size, y * self.cell_size, 
                             self.cell_size, self.cell_size))
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw game over message
        if self.game_over:
            game_over_text = self.font.render("Game Over! Press SPACE to restart", True, self.WHITE)
            text_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(10)  # Adjust game speed (10 FPS)

def main():
    game = SnakeGame()
    game.run()

if __name__ == "__main__":
    main()