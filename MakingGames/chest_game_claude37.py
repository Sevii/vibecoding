# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pygame",
# ]
# ///

import pygame
import random
import sys
from collections import deque

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
PLAYER_SIZE = 30
CHEST_SIZE = 30
PLAYER_SPEED = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Treasure Hunter")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont('Arial', 24)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.gold = 0
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.is_alive = True
        self.wall_break_cooldown = 0
    
    def move(self, dx, dy, walls):
        # Check for collisions before moving
        new_rect = self.rect.copy()
        new_rect.x += dx
        new_rect.y += dy
        
        # Check if new position would collide with any wall
        collision = False
        for wall in walls:
            if new_rect.colliderect(wall.rect):
                collision = True
                break
        
        # Only move if there's no collision
        if not collision:
            self.x += dx
            self.y += dy
            self.rect.x = self.x
            self.rect.y = self.y
    
    def break_wall(self, walls):
        # Create a slightly larger rect to check for adjacent walls
        check_rect = self.rect.inflate(TILE_SIZE * 0.3, TILE_SIZE * 0.3)
        
        # Find walls that collide with the check rect
        nearby_walls = [wall for wall in walls if check_rect.colliderect(wall.rect)]
        
        # If there are nearby walls and player has enough gold
        if nearby_walls and self.gold >= 10 and self.wall_break_cooldown <= 0:
            # Sort walls by distance to player center
            player_center = (self.x + self.width/2, self.y + self.height/2)
            
            def distance_to_wall(wall):
                wall_center = (wall.rect.x + wall.rect.width/2, 
                               wall.rect.y + wall.rect.height/2)
                return ((wall_center[0] - player_center[0])**2 + 
                        (wall_center[1] - player_center[1])**2)**0.5
            
            # Get the closest wall
            nearby_walls.sort(key=distance_to_wall)
            wall_to_break = nearby_walls[0]
            
            # Remove the wall
            walls.remove(wall_to_break)
            
            # Deduct gold
            self.gold -= 10
            
            # Set cooldown (45 frames = 0.75 seconds at 60fps)
            self.wall_break_cooldown = 45
            
            # Create a breaking effect (simple animation)
            return wall_to_break.rect.topleft
        
        return None
    
    def update(self):
        # Update cooldown
        if self.wall_break_cooldown > 0:
            self.wall_break_cooldown -= 1
    
    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)
        # Draw a simple face on the player
        pygame.draw.circle(screen, WHITE, (self.x + 10, self.y + 10), 5)
        pygame.draw.circle(screen, WHITE, (self.x + 20, self.y + 10), 5)
        pygame.draw.arc(screen, WHITE, (self.x + 5, self.y + 15, 20, 10), 0, 3.14, 2)

class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
        # Add some texture to walls
        for i in range(0, self.rect.width, 10):
            for j in range(0, self.rect.height, 10):
                if (i + j) % 20 == 0:
                    pygame.draw.rect(screen, (100, 100, 100), 
                                    (self.rect.x + i, self.rect.y + j, 5, 5))

class Chest:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = CHEST_SIZE
        self.height = CHEST_SIZE
        self.gold = random.randint(5, 20)
        self.is_open = False
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def open(self):
        self.is_open = True
    
    def draw(self):
        if not self.is_open:
            # Closed chest
            pygame.draw.rect(screen, BROWN, self.rect)
            # Chest lid
            pygame.draw.rect(screen, (110, 50, 0), 
                            (self.x, self.y, self.width, self.height // 3))
            # Lock
            pygame.draw.rect(screen, GOLD, 
                            (self.x + self.width // 2 - 5, self.y + self.height // 3 - 5, 10, 10))
        else:
            # Open chest
            pygame.draw.rect(screen, BROWN, self.rect)
            # Open lid
            pygame.draw.rect(screen, (110, 50, 0), 
                            (self.x, self.y - self.height // 4, self.width, self.height // 3))
            # Gold inside
            pygame.draw.circle(screen, GOLD, 
                            (self.x + self.width // 2, self.y + self.height // 2 + 5), 10)


class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 0.65  # Make monster even smaller
        self.height = TILE_SIZE * 0.65  # Make monster even smaller
        self.speed = PLAYER_SPEED * 0.75  # Slightly slower than player
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.path = []
        self.path_update_timer = 0
        self.path_update_delay = 30  # Update path every 30 frames
    
    def find_path(self, maze, player_pos, walls):
        """Use breadth-first search to find a path to the player"""
        # Convert positions to grid coordinates
        start_x, start_y = int(self.x / TILE_SIZE), int(self.y / TILE_SIZE)
        target_x, target_y = int(player_pos[0] / TILE_SIZE), int(player_pos[1] / TILE_SIZE)
        
        # Create a grid representation
        grid_width = SCREEN_WIDTH // TILE_SIZE
        grid_height = SCREEN_HEIGHT // TILE_SIZE
        grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
        
        # Mark walls in the grid
        for wall in walls:
            wall_x, wall_y = int(wall.rect.x / TILE_SIZE), int(wall.rect.y / TILE_SIZE)
            if 0 <= wall_x < grid_width and 0 <= wall_y < grid_height:
                grid[wall_y][wall_x] = 1
        
        # BFS queue
        queue = deque([(start_x, start_y)])
        visited = {(start_x, start_y): None}  # Map position to its predecessor
        
        # Directions: right, down, left, up
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        
        # BFS until we find the target or exhaust all options
        found = False
        while queue and not found:
            x, y = queue.popleft()
            
            if (x, y) == (target_x, target_y):
                found = True
                break
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                # Check if the position is valid
                if (0 <= nx < grid_width and 0 <= ny < grid_height and 
                    grid[ny][nx] == 0 and (nx, ny) not in visited):
                    queue.append((nx, ny))
                    visited[(nx, ny)] = (x, y)
        
        # Reconstruct path if found
        path = []
        if found:
            current = (target_x, target_y)
            while current != (start_x, start_y):
                path.append(current)
                current = visited[current]
            path.reverse()
        
        # Convert grid coordinates back to pixel coordinates
        return [(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2) for x, y in path]
    
    def move(self, player, walls, frame_count):
        """Move the monster towards the player following the path"""
        # Update path periodically
        if frame_count % self.path_update_delay == 0:
            self.path = self.find_path(None, (player.x, player.y), walls)
        
        # If we have a path, follow it
        if self.path:
            # Get the next point in the path
            target_x, target_y = self.path[0]
            
            # Calculate direction vector
            dx = target_x - (self.x + self.width // 2)
            dy = target_y - (self.y + self.height // 2)
            
            # Normalize
            distance = max(1, (dx**2 + dy**2)**0.5)
            dx = dx / distance * self.speed
            dy = dy / distance * self.speed
            
            # Move towards next point
            new_rect = self.rect.copy()
            new_rect.x += dx
            new_rect.y += dy
            
            # Check for wall collisions
            collision = False
            for wall in walls:
                if new_rect.colliderect(wall.rect):
                    collision = True
                    break
            
            # Only move if there's no collision
            if not collision:
                self.x += dx
                self.y += dy
                self.rect.x = self.x
                self.rect.y = self.y
            
            # If we're close to the target point, remove it from the path
            if ((self.x + self.width // 2 - target_x)**2 + 
                (self.y + self.height // 2 - target_y)**2) < (self.speed * 2)**2:
                self.path.pop(0)
    
    def check_collision(self, player):
        """Check if the monster has caught the player"""
        return self.rect.colliderect(player.rect)
    
    def draw(self):
        """Draw the monster as a bank-shaped entity"""
        # Main building
        pygame.draw.rect(screen, RED, self.rect)
        
        # Roof/top part
        roof_points = [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width // 2, self.y - self.height // 4)
        ]
        pygame.draw.polygon(screen, RED, roof_points)
        
        # Columns
        column_width = self.width // 6
        column_height = self.height // 2
        column_y = self.y + self.height - column_height
        
        # Left column
        pygame.draw.rect(screen, WHITE, (self.x, column_y, column_width, column_height))
        # Right column
        pygame.draw.rect(screen, WHITE, (self.x + self.width - column_width, column_y, column_width, column_height))
        # Middle column
        pygame.draw.rect(screen, WHITE, (self.x + (self.width - column_width) // 2, column_y, column_width, column_height))
        
        # Door
        door_width = self.width // 3
        door_height = self.height // 3
        door_x = self.x + (self.width - door_width) // 2
        door_y = self.y + self.height - door_height
        pygame.draw.rect(screen, BLACK, (door_x, door_y, door_width, door_height))
        
        # Eyes (angry)
        eye_radius = 3
        pygame.draw.circle(screen, BLACK, (self.x + self.width // 3, self.y + self.height // 3), eye_radius)
        pygame.draw.circle(screen, BLACK, (self.x + 2 * self.width // 3, self.y + self.height // 3), eye_radius)
        
        # Mouth (angry)
        mouth_y = self.y + self.height // 2
        pygame.draw.line(screen, BLACK, (self.x + self.width // 4, mouth_y), 
                         (self.x + 3 * self.width // 4, mouth_y), 2)

def generate_maze(width, height):
    """Generate a maze using a randomized depth-first search algorithm"""
    # Initialize the grid
    grid = [[1 for _ in range(width)] for _ in range(height)]
    
    # Start from a random cell
    start_x, start_y = random.randint(1, width-2), random.randint(1, height-2)
    grid[start_y][start_x] = 0
    
    # Stack for backtracking
    stack = [(start_x, start_y)]
    
    # Directions: right, down, left, up
    directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]
    
    while stack:
        x, y = stack[-1]
        
        # Get unvisited neighbors
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width-1 and 1 <= ny < height-1 and grid[ny][nx] == 1:
                neighbors.append((nx, ny, dx, dy))
        
        if neighbors:
            # Choose a random unvisited neighbor
            nx, ny, dx, dy = random.choice(neighbors)
            
            # Remove the wall between current cell and chosen neighbor
            grid[y + dy//2][x + dx//2] = 0
            grid[ny][nx] = 0
            
            # Push the neighbor to the stack
            stack.append((nx, ny))
        else:
            # Backtrack
            stack.pop()
    
    return grid

def create_level():
    # Define the maze grid size
    maze_width = SCREEN_WIDTH // TILE_SIZE
    maze_height = SCREEN_HEIGHT // TILE_SIZE
    
    # Generate the maze
    maze = generate_maze(maze_width, maze_height)
    
    walls = []
    possible_chest_positions = []
    
    # Create walls from the maze
    for y in range(maze_height):
        for x in range(maze_width):
            if maze[y][x] == 1:
                walls.append(Wall(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            else:
                # Add empty spaces as possible chest positions
                possible_chest_positions.append((x * TILE_SIZE, y * TILE_SIZE))
    
    # Create some chests at random empty positions
    chests = []
    chest_count = min(10, len(possible_chest_positions))
    chest_positions = random.sample(possible_chest_positions, chest_count)
    
    for x, y in chest_positions:
        chests.append(Chest(x + (TILE_SIZE - CHEST_SIZE) // 2, 
                           y + (TILE_SIZE - CHEST_SIZE) // 2))
    
    # Find a good starting position for the player
    for pos in possible_chest_positions:
        if pos not in chest_positions:
            player_x, player_y = pos
            player_x += (TILE_SIZE - PLAYER_SIZE) // 2
            player_y += (TILE_SIZE - PLAYER_SIZE) // 2
            break
    
    player = Player(player_x, player_y)
    
    # Find a starting position for the monster far from the player
    monster_pos = None
    max_distance = 0
    for pos in possible_chest_positions:
        if pos not in chest_positions:
            distance = ((pos[0] - player_x) ** 2 + (pos[1] - player_y) ** 2) ** 0.5
            if distance > max_distance:
                max_distance = distance
                monster_pos = pos
    
    monster = None
    if monster_pos:
        monster = Monster(monster_pos[0], monster_pos[1])
    
    return player, walls, chests, monster

def main():
    # Create the level
    player, walls, chests, monster = create_level()
    
    # Frame counter
    frame_count = 0
    
    # Game state
    game_over = False
    win = False
    
    # Wall break effect
    break_effect = None
    break_effect_duration = 0
    
    # Main game loop
    running = True
    while running:
        # Increment frame counter
        frame_count += 1
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (game_over or win):
                    # Restart the game
                    player, walls, chests, monster = create_level()
                    frame_count = 0
                    game_over = False
                    win = False
                elif event.key == pygame.K_SPACE and not game_over and not win:
                    # Try to break a wall
                    broken_wall_pos = player.break_wall(walls)
                    if broken_wall_pos:
                        break_effect = broken_wall_pos
                        break_effect_duration = 15  # Show effect for 15 frames
        
        # Get key states
        keys = pygame.key.get_pressed()
        
        # Process game logic only if the game is not over
        if not game_over and not win:
            # Update player (cooldowns, etc)
            player.update()
            
            # Handle player movement
            dx, dy = 0, 0
            if keys[pygame.K_LEFT]:
                dx = -player.speed
            if keys[pygame.K_RIGHT]:
                dx = player.speed
            if keys[pygame.K_UP]:
                dy = -player.speed
            if keys[pygame.K_DOWN]:
                dy = player.speed
            
            player.move(dx, dy, walls)
            
            # Move the monster
            monster.move(player, walls, frame_count)
            
            # Check if monster caught the player
            if monster.check_collision(player):
                game_over = True
                player.is_alive = False
            
            # Check for chests
            for chest in chests:
                if not chest.is_open and player.rect.colliderect(chest.rect):
                    chest.open()
                    player.gold += chest.gold
                    print(f"Found {chest.gold} gold! Total: {player.gold}")
            
            # Check win condition (all chests opened)
            if all(chest.is_open for chest in chests):
                win = True
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw walls
        for wall in walls:
            wall.draw()
        
        # Draw break effect
        if break_effect and break_effect_duration > 0:
            # Create explosion-like particles
            for _ in range(5):
                x = break_effect[0] + random.randint(0, TILE_SIZE)
                y = break_effect[1] + random.randint(0, TILE_SIZE)
                size = random.randint(3, 10)
                color_val = random.randint(200, 255)
                color = (color_val, color_val, 0)  # Yellow-ish
                pygame.draw.circle(screen, color, (x, y), size)
            
            break_effect_duration -= 1
            if break_effect_duration <= 0:
                break_effect = None
        
        # Draw chests
        for chest in chests:
            chest.draw()
        
        # Draw monster
        monster.draw()
        
        # Draw player if alive
        if player.is_alive:
            player.draw()
        
        # Draw UI
        gold_text = font.render(f"Gold: {player.gold}", True, GOLD)
        screen.blit(gold_text, (10, 10))
        
        # Draw wall break ability info
        if player.wall_break_cooldown > 0:
            cooldown_text = font.render(f"Wall Break Cooldown: {player.wall_break_cooldown // 15 + 1}s", True, WHITE)
            screen.blit(cooldown_text, (10, 40))
        else:
            if player.gold >= 10:
                ability_text = font.render("Press SPACE to break a wall (Cost: 10 Gold)", True, GREEN)
            else:
                ability_text = font.render("Need 10 Gold to break walls", True, (150, 150, 150))
            screen.blit(ability_text, (10, 40))
        
        # Display messages based on game state
        if game_over:
            game_over_text = font.render("GAME OVER! The bank monster caught you!", True, RED)
            restart_text = font.render("Press R to play again", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 20))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20))
        elif win:
            win_text = font.render(f"YOU WON! You collected {player.gold} gold!", True, GOLD)
            restart_text = font.render("Press R to play again or ESC to exit", True, WHITE)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 20))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20))
            if keys[pygame.K_ESCAPE]:
                running = False
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()