import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 50
NUM_ROWS, NUM_COLS = SCREEN_HEIGHT // TILE_SIZE, SCREEN_WIDTH // TILE_SIZE
PLAYER_SPEED = 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Game")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED

# Obstacle class (rocks, stalagmites)
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Chest class (contains gold)
class Chest(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Create groups of sprites
all_sprites = pygame.sprite.Group()
obstacles_group = pygame.sprite.Group()
chests_group = pygame.sprite.Group()

# Create the player
player = Player()
all_sprites.add(player)

# Generate obstacles and chests randomly in the maze
for _ in range(50):
    x, y = random.randint(0, NUM_COLS - 1) * TILE_SIZE, random.randint(0, NUM_ROWS - 1) * TILE_SIZE
    obstacle = Obstacle(x, y)
    all_sprites.add(obstacle)
    obstacles_group.add(obstacle)

for _ in range(5):
    x, y = random.randint(0, NUM_COLS - 1) * TILE_SIZE, random.randint(0, NUM_ROWS - 1) * TILE_SIZE
    chest = Chest(x, y)
    all_sprites.add(chest)
    chests_group.add(chest)

# Game loop
running = True
clock = pygame.time.Clock()
score = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement and obstacle collision detection
    keys = pygame.key.get_pressed()
    player.update(keys)
    
    # Check for collisions with obstacles
    if pygame.sprite.spritecollideany(player, obstacles_group):
        print("Game Over! You hit an obstacle.")
        running = False

    # Collect gold from chests
    if pygame.sprite.spritecollideany(player, chests_group):
        score += 1
        print(f"Collected Gold! Total Score: {score}")
        for chest in pygame.sprite.spritecollide(player, chests_group, True):
            all_sprites.remove(chest)

    # Drawing
    screen.fill(BLACK)
    all_sprites.draw(screen)
    pygame.display.flip()

    clock.tick(30)  # Limit frames per second

pygame.quit()
