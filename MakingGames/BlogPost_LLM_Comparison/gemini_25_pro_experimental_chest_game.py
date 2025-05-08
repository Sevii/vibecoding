import pygame
import random

# --- Constants ---
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GREY = (128, 128, 128)
GOLD_COLOR = (255, 215, 0)
PLAYER_COLOR = (0, 128, 255)
GREEN = (0, 255, 0) # For messages

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40 # Size of each grid tile

# Player settings
PLAYER_SPEED = 5

# Maze dimensions (in tiles)
MAZE_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAZE_HEIGHT = (SCREEN_HEIGHT - 80) // TILE_SIZE # Leave space for score display

# --- Helper Functions ---
def draw_text(surface, text, size, x, y, color):
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# --- Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE // 2, TILE_SIZE // 2])
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.gold = 0

    def update(self, pressed_keys, walls):
        old_x = self.rect.x
        old_y = self.rect.y

        if pressed_keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if pressed_keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if pressed_keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if pressed_keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED

        # Keep player on screen (simple boundary)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT - 80: # Account for score area
            self.rect.bottom = SCREEN_HEIGHT - 80

        # Collision with walls
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                # If moved in x, revert x
                if self.rect.x != old_x:
                    self.rect.x = old_x
                # If moved in y, revert y
                if self.rect.y != old_y:
                    self.rect.y = old_y
                # A more refined collision response would be to place player adjacent to wall
                # but this works for now.

    def collect_gold(self, amount):
        self.gold += amount
        print(f"Collected {amount} gold! Total: {self.gold}")

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, wall_type="rock"):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        if wall_type == "rock":
            self.image.fill(GREY) # Rocks
        else: # stalagmite
            self.image.fill(BROWN) # Stalagmites
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class Chest(pygame.sprite.Sprite):
    def __init__(self, x, y, gold_amount=10):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE - 10, TILE_SIZE - 10])
        self.image.fill(GOLD_COLOR)
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2) # Border
        self.rect = self.image.get_rect()
        self.rect.center = (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)
        self.gold_amount = gold_amount
        self.is_opened = False

    def open_chest(self, player):
        if not self.is_opened:
            player.collect_gold(self.gold_amount)
            self.is_opened = True
            self.image.fill(BROWN) # Change color to show it's opened
            pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2)
            return True
        return False

# --- Maze Generation (Simple Randomised DFS) ---
def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)] # 1 is wall, 0 is path

    def is_valid(x, y):
        return 0 <= y < height and 0 <= x < width

    def carve_passages(cx, cy):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)] # S, E, N, W
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = cx + dx * 2, cy + dy * 2 # Next cell (2 steps away)
            if is_valid(nx, ny) and maze[ny][nx] == 1:
                maze[cy + dy][cx + dx] = 0 # Carve wall in between
                maze[ny][nx] = 0         # Carve next cell
                carve_passages(nx, ny)

    # Start carving from a random odd position to ensure wall spacing
    start_x, start_y = random.randrange(1, width, 2), random.randrange(1, height, 2)
    maze[start_y][start_x] = 0
    carve_passages(start_x, start_y)

    # Ensure entrance and potentially an exit (though not strictly needed for this game)
    maze[1][0] = 0 # Entrance at top-left (ish)
    # maze[height-2][width-1] = 0 # Potential exit

    # Add some more random open spaces (rocks/stalagmites will be placed later)
    for _ in range(width * height // 10): # Open up about 10% more cells
        rx, ry = random.randrange(1, width - 1), random.randrange(1, height - 1)
        if maze[ry][rx] == 1: # If it's a wall
             # Check neighbors to avoid creating tiny isolated rooms if opening a wall next to path
            path_neighbors = 0
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                if is_valid(rx+dx, ry+dy) and maze[ry+dy][rx+dx] == 0:
                    path_neighbors +=1
            if path_neighbors > 0 and path_neighbors < 3 : # Avoid completely isolated or too open
                maze[ry][rx] = 0


    return maze

# --- Game Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Gold Collector")
clock = pygame.time.Clock()

# --- Game Setup ---
# Create sprite groups
all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()
chests = pygame.sprite.Group()

# Generate maze layout
maze_layout = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)

# Populate walls and find open spaces for player and chests
open_spaces = []
for r, row in enumerate(maze_layout):
    for c, tile in enumerate(row):
        if tile == 1:
            wall_type = "rock" if random.random() > 0.3 else "stalagmite"
            wall = Wall(c, r, wall_type)
            all_sprites.add(wall)
            walls.add(wall)
        else:
            open_spaces.append((c, r))

# Place player
if not open_spaces: # Should not happen with proper maze gen
    player_start_x, player_start_y = TILE_SIZE, TILE_SIZE
else:
    # Try to place player near the entrance (1,0) of the maze grid
    player_spawn_tile = (1,1) # Tile (1,0) is path, (1,1) should be too
    if maze_layout[player_spawn_tile[1]][player_spawn_tile[0]] == 0:
         player_start_x = player_spawn_tile[0] * TILE_SIZE + TILE_SIZE // 2
         player_start_y = player_spawn_tile[1] * TILE_SIZE + TILE_SIZE // 2
         if (player_spawn_tile[0], player_spawn_tile[1]) in open_spaces:
            open_spaces.remove((player_spawn_tile[0],player_spawn_tile[1]))
    else: # Fallback if (1,1) is not open
        player_start_tile_coords = random.choice(open_spaces)
        open_spaces.remove(player_start_tile_coords)
        player_start_x = player_start_tile_coords[0] * TILE_SIZE + TILE_SIZE // 2
        player_start_y = player_start_tile_coords[1] * TILE_SIZE + TILE_SIZE // 2


player = Player(player_start_x, player_start_y)
all_sprites.add(player)

# Place chests
num_chests = 5
for _ in range(num_chests):
    if open_spaces:
        chest_pos = random.choice(open_spaces)
        open_spaces.remove(chest_pos) # Ensure chests don't overlap
        gold_in_chest = random.choice([10, 20, 30, 5, 50])
        chest = Chest(chest_pos[0], chest_pos[1], gold_in_chest)
        all_sprites.add(chest)
        chests.add(chest)
    else:
        break # No more open spaces for chests

# --- Game Loop ---
running = True
game_over = False
win_message_timer = 0

while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if game_over and event.key == pygame.K_r: # Restart game
                # Reset and re-initialize game state
                all_sprites.empty()
                walls.empty()
                chests.empty()
                open_spaces.clear()

                maze_layout = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
                for r, row in enumerate(maze_layout):
                    for c, tile in enumerate(row):
                        if tile == 1:
                            wall_type = "rock" if random.random() > 0.3 else "stalagmite"
                            wall = Wall(c, r, wall_type)
                            all_sprites.add(wall)
                            walls.add(wall)
                        else:
                            open_spaces.append((c, r))
                
                if not open_spaces:
                    player_start_x, player_start_y = TILE_SIZE, TILE_SIZE
                else:
                    player_spawn_tile = (1,1) 
                    if maze_layout[player_spawn_tile[1]][player_spawn_tile[0]] == 0:
                         player_start_x = player_spawn_tile[0] * TILE_SIZE + TILE_SIZE // 2
                         player_start_y = player_spawn_tile[1] * TILE_SIZE + TILE_SIZE // 2
                         if (player_spawn_tile[0], player_spawn_tile[1]) in open_spaces:
                            open_spaces.remove((player_spawn_tile[0],player_spawn_tile[1]))
                    else: 
                        player_start_tile_coords = random.choice(open_spaces)
                        open_spaces.remove(player_start_tile_coords)
                        player_start_x = player_start_tile_coords[0] * TILE_SIZE + TILE_SIZE // 2
                        player_start_y = player_start_tile_coords[1] * TILE_SIZE + TILE_SIZE // 2

                player = Player(player_start_x, player_start_y)
                all_sprites.add(player)

                for _ in range(num_chests):
                    if open_spaces:
                        chest_pos = random.choice(open_spaces)
                        open_spaces.remove(chest_pos)
                        gold_in_chest = random.choice([10, 20, 30, 5, 50])
                        chest = Chest(chest_pos[0], chest_pos[1], gold_in_chest)
                        all_sprites.add(chest)
                        chests.add(chest)
                    else:
                        break
                game_over = False
                win_message_timer = 0


    if not game_over:
        # --- Update ---
        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys, walls)

        # Check for chest collisions
        opened_chests_this_frame = pygame.sprite.spritecollide(player, chests, False)
        for chest in opened_chests_this_frame:
            if not chest.is_opened:
                if chest.open_chest(player):
                    # Optional: remove chest after opening, or just change its state
                    # chests.remove(chest)
                    # all_sprites.remove(chest)
                    pass # Already handled in open_chest

        # Check if all chests are opened
        if all(c.is_opened for c in chests):
            game_over = True
            win_message_timer = pygame.time.get_ticks() # Start timer for win message

    # --- Drawing ---
    screen.fill(BLACK) # Background for the maze area

    all_sprites.draw(screen)

    # Score/Gold display area
    score_area_rect = pygame.Rect(0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80)
    pygame.draw.rect(screen, GREY, score_area_rect)
    draw_text(screen, f"Gold: {player.gold}", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 65, GOLD_COLOR)
    if not chests: # Or if all chests are opened
         draw_text(screen, "Find the chests!", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, WHITE)
    else:
        remaining_chests = sum(1 for c in chests if not c.is_opened)
        if remaining_chests > 0 :
             draw_text(screen, f"Chests remaining: {remaining_chests}", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, WHITE)
        else:
             draw_text(screen, "All chests collected!", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, GREEN)


    if game_over:
        if all(c.is_opened for c in chests): # Win condition
            current_time = pygame.time.get_ticks()
            if current_time - win_message_timer < 5000: # Display for 5 seconds
                draw_text(screen, "Congratulations! You collected all the gold!", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, GREEN)
            draw_text(screen, "Press 'R' to Play Again or ESC to Quit", 25, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, WHITE)
        # You could add a lose condition here if needed

    pygame.display.flip() # Update the full screen

    # --- Maintain frame rate ---
    clock.tick(60) # 60 FPS

pygame.quit()