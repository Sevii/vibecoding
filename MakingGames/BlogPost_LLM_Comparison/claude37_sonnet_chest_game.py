import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
PLAYER_SPEED = 5
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
GREEN = (0, 128, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cave Treasure Hunter")
clock = pygame.time.Clock()

# Define game entities
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE - 10, TILE_SIZE - 10))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.gold = 0
        
    def update(self, obstacles):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            dx = PLAYER_SPEED
        if keys[pygame.K_UP]:
            dy = -PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            dy = PLAYER_SPEED
            
        # Test horizontal movement
        self.rect.x += dx
        collision = pygame.sprite.spritecollide(self, obstacles, False)
        if collision:
            self.rect.x -= dx
            
        # Test vertical movement
        self.rect.y += dy
        collision = pygame.sprite.spritecollide(self, obstacles, False)
        if collision:
            self.rect.y -= dy
            
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, is_stalagmite=False):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GRAY if is_stalagmite else BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Chest(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GOLD)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.gold_amount = random.randint(10, 50)

def generate_maze(width, height):
    # Simple maze generation
    grid = [[0 for _ in range(width)] for _ in range(height)]
    
    # Add borders
    for x in range(width):
        grid[0][x] = 1
        grid[height-1][x] = 1
    for y in range(height):
        grid[y][0] = 1
        grid[y][width-1] = 1
    
    # Add random obstacles
    for _ in range(int(width * height * 0.2)):
        x = random.randint(1, width-2)
        y = random.randint(1, height-2)
        if grid[y][x] == 0:
            grid[y][x] = 1
    
    # Add some paths to ensure traversability
    for y in range(2, height-2, 2):
        for x in range(2, width-2, 2):
            grid[y][x] = 0
    
    return grid

def setup_game():
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    chests = pygame.sprite.Group()
    
    # Generate maze
    grid_width = WIDTH // TILE_SIZE
    grid_height = HEIGHT // TILE_SIZE
    maze = generate_maze(grid_width, grid_height)
    
    # Add objects based on maze
    for y in range(grid_height):
        for x in range(grid_width):
            if maze[y][x] == 1:
                obstacle = Obstacle(x * TILE_SIZE, y * TILE_SIZE, random.choice([True, False]))
                obstacles.add(obstacle)
                all_sprites.add(obstacle)
    
    # Add chests in empty spaces
    for _ in range(8):
        while True:
            x = random.randint(1, grid_width-2)
            y = random.randint(1, grid_height-2)
            if maze[y][x] == 0:
                chest = Chest(x * TILE_SIZE, y * TILE_SIZE)
                chests.add(chest)
                all_sprites.add(chest)
                break
    
    # Add player in empty space
    player_placed = False
    while not player_placed:
        x = random.randint(1, grid_width-2)
        y = random.randint(1, grid_height-2)
        if maze[y][x] == 0:
            player = Player(x * TILE_SIZE, y * TILE_SIZE)
            all_sprites.add(player)
            player_placed = True
    
    return all_sprites, obstacles, chests, player

def main():
    all_sprites, obstacles, chests, player = setup_game()
    font = pygame.font.SysFont(None, 36)
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update
        all_sprites.update(obstacles)
        
        # Check for chest collection
        collected_chests = pygame.sprite.spritecollide(player, chests, True)
        for chest in collected_chests:
            player.gold += chest.gold_amount
        
        # Draw
        screen.fill(BLACK)
        all_sprites.draw(screen)
        
        # Draw HUD
        gold_text = font.render(f"Gold: {player.gold}", True, GOLD)
        screen.blit(gold_text, (10, 10))
        
        # Check win condition
        if len(chests) == 0:
            win_text = font.render(f"You collected all the gold! Total: {player.gold}", True, WHITE)
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()