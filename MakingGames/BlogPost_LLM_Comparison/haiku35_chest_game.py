import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
GREEN = (0, 255, 0)

# Player settings
PLAYER_SPEED = 5

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.gold_collected = 0

    def move(self, dx, dy, obstacles):
        # Temporary move
        self.rect.x += dx
        self.rect.y += dy

        # Check for collisions
        collision = pygame.sprite.spritecollide(self, obstacles, False)
        if collision:
            # Revert move if collision occurs
            self.rect.x -= dx
            self.rect.y -= dy

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, is_rock=True):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Chest(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(GOLD)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.gold_value = random.randint(10, 50)

def create_maze(num_obstacles=30, num_chests=5):
    obstacles = pygame.sprite.Group()
    chests = pygame.sprite.Group()

    # Create borders
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        obstacles.add(Obstacle(x, 0))
        obstacles.add(Obstacle(x, SCREEN_HEIGHT - GRID_SIZE))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        obstacles.add(Obstacle(0, y))
        obstacles.add(Obstacle(SCREEN_WIDTH - GRID_SIZE, y))

    # Create random obstacles
    for _ in range(num_obstacles):
        x = random.randrange(GRID_SIZE, SCREEN_WIDTH - GRID_SIZE, GRID_SIZE)
        y = random.randrange(GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE)
        obstacles.add(Obstacle(x, y))

    # Create chests
    for _ in range(num_chests):
        while True:
            x = random.randrange(GRID_SIZE, SCREEN_WIDTH - GRID_SIZE, GRID_SIZE)
            y = random.randrange(GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE)
            # Ensure chest is not on an obstacle
            chest = Chest(x, y)
            if not pygame.sprite.spritecollideany(chest, obstacles):
                chests.add(chest)
                break

    return obstacles, chests

def main():
    # Setup the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Gold Collector")
    clock = pygame.time.Clock()

    # Create font for displaying gold
    font = pygame.font.Font(None, 36)

    # Create game objects
    obstacles, chests = create_maze()

    # Create player
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    all_sprites = pygame.sprite.Group(player)
    all_sprites.add(obstacles)
    all_sprites.add(chests)

    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Key handling for movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-PLAYER_SPEED, 0, obstacles)
        if keys[pygame.K_RIGHT]:
            player.move(PLAYER_SPEED, 0, obstacles)
        if keys[pygame.K_UP]:
            player.move(0, -PLAYER_SPEED, obstacles)
        if keys[pygame.K_DOWN]:
            player.move(0, PLAYER_SPEED, obstacles)

        # Check for chest collection
        collected_chests = pygame.sprite.spritecollide(player, chests, True)
        for chest in collected_chests:
            player.gold_collected += chest.gold_value

        # Drawing
        screen.fill(WHITE)
        
        # Draw obstacles
        for obstacle in obstacles:
            screen.blit(obstacle.image, obstacle.rect)
        
        # Draw chests
        for chest in chests:
            screen.blit(chest.image, chest.rect)
        
        # Draw player
        screen.blit(player.image, player.rect)

        # Draw gold count
        gold_text = font.render(f"Gold: {player.gold_collected}", True, BLACK)
        screen.blit(gold_text, (10, 10))

        # Update display
        pygame.display.flip()

        # Control game speed
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
