import pygame
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GOLD = (255, 215, 0)
GREEN = (0, 255, 0)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Gold Collector")

# Load assets (placeholder rectangles for now)
player_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
player_img.fill(GREEN)
rock_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
rock_img.fill(GRAY)
stalagmite_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
stalagmite_img.fill((139, 69, 19))
chest_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
chest_img.fill(GOLD)

# Map Tiles
EMPTY, ROCK, STALAGMITE, CHEST = 0, 1, 2, 3

def generate_maze():
    grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

    # Add borders
    for x in range(COLS):
        grid[0][x] = ROCK
        grid[ROWS - 1][x] = ROCK
    for y in range(ROWS):
        grid[y][0] = ROCK
        grid[y][COLS - 1] = ROCK

    # Add random rocks and stalagmites
    for _ in range(150):
        x, y = random.randint(1, COLS - 2), random.randint(1, ROWS - 2)
        grid[y][x] = random.choice([ROCK, STALAGMITE])

    # Add chests
    for _ in range(10):
        while True:
            x, y = random.randint(1, COLS - 2), random.randint(1, ROWS - 2)
            if grid[y][x] == EMPTY:
                grid[y][x] = CHEST
                break

    return grid

def draw_grid(grid, player_pos):
    for y in range(ROWS):
        for x in range(COLS):
            tile = grid[y][x]
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if tile == ROCK:
                screen.blit(rock_img, rect)
            elif tile == STALAGMITE:
                screen.blit(stalagmite_img, rect)
            elif tile == CHEST:
                screen.blit(chest_img, rect)

    # Draw player
    px, py = player_pos
    screen.blit(player_img, (px * TILE_SIZE, py * TILE_SIZE))

def main():
    clock = pygame.time.Clock()
    grid = generate_maze()
    player_pos = [1, 1]
    gold_collected = 0
    font = pygame.font.SysFont(None, 36)

    running = True
    while running:
        screen.fill(BLACK)
        draw_grid(grid, player_pos)

        # Draw HUD
        hud = font.render(f"Gold Collected: {gold_collected}", True, WHITE)
        screen.blit(hud, (10, 10))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]: dx = -1
        if keys[pygame.K_RIGHT]: dx = 1
        if keys[pygame.K_UP]: dy = -1
        if keys[pygame.K_DOWN]: dy = 1

        new_x = player_pos[0] + dx
        new_y = player_pos[1] + dy

        if 0 <= new_x < COLS and 0 <= new_y < ROWS:
            if grid[new_y][new_x] != ROCK and grid[new_y][new_x] != STALAGMITE:
                player_pos = [new_x, new_y]
                if grid[new_y][new_x] == CHEST:
                    gold_collected += 1
                    grid[new_y][new_x] = EMPTY

    pygame.quit()

if __name__ == "__main__":
    main()
