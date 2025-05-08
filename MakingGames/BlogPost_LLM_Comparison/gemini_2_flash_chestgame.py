import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gold Miner")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
brown = (139, 69, 19)
gray = (105, 105, 105)
gold_color = (255, 215, 0)

# Player properties
player_size = 20
player_x = 50
player_y = 50
player_speed = 5

# Rock properties
rock_size = 30
num_rocks = 20
rocks = []
for _ in range(num_rocks):
    rock_x = random.randint(100, screen_width - 100 - rock_size)
    rock_y = random.randint(100, screen_height - 100 - rock_size)
    rocks.append(pygame.Rect(rock_x, rock_y, rock_size, rock_size))

# Stalagmite properties
stalagmite_width = 20
stalagmite_height = 50
num_stalagmites = 15
stalagmites = []
for _ in range(num_stalagmites):
    stalagmite_x = random.randint(100, screen_width - 100 - stalagmite_width)
    stalagmite_y = random.randint(100, screen_height - 100 - stalagmite_height)
    stalagmites.append(pygame.Rect(stalagmite_x, stalagmite_y, stalagmite_width, stalagmite_height))

# Chest properties
chest_size = 25
num_chests = 5
chests = []
for _ in range(num_chests):
    chest_x = random.randint(100, screen_width - 100 - chest_size)
    chest_y = random.randint(100, screen_height - 100 - chest_size)
    chests.append(pygame.Rect(chest_x, chest_y, chest_size, chest_size))

# Gold collected
gold_count = 0

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    new_player_rect = player_rect.copy()

    if keys[pygame.K_LEFT]:
        new_player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]:
        new_player_rect.x += player_speed
    if keys[pygame.K_UP]:
        new_player_rect.y -= player_speed
    if keys[pygame.K_DOWN]:
        new_player_rect.y += player_speed

    # Collision detection with rocks
    collision = False
    for rock in rocks:
        if new_player_rect.colliderect(rock):
            collision = True
            break
    if not collision:
        player_rect.x = new_player_rect.x
        player_rect.y = new_player_rect.y

    # Collision detection with stalagmites
    collision = False
    for stalagmite in stalagmites:
        if player_rect.colliderect(stalagmite):
            collision = True
            break
    if collision:
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size) # Reset position

    # Collect gold
    for i, chest in enumerate(chests):
        if player_rect.colliderect(chest):
            gold_count += 1
            chests.pop(i)
            break

    # Drawing
    screen.fill(white)

    # Draw rocks
    for rock in rocks:
        pygame.draw.rect(screen, gray, rock)

    # Draw stalagmites
    for stalagmite in stalagmites:
        pygame.draw.rect(screen, brown, stalagmite)

    # Draw chests
    for chest in chests:
        pygame.draw.rect(screen, gold_color, chest)

    # Draw player
    pygame.draw.rect(screen, black, player_rect)

    # Display gold count
    font = pygame.font.Font(None, 30)
    text = font.render(f"Gold: {gold_count}", True, black)
    screen.blit(text, (10, 10))

    pygame.display.flip()

pygame.quit()