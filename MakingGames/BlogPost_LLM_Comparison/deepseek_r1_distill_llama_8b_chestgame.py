import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game constants
屏幕宽 = 800
屏幕高 = 600
背景色 = (255, 0, 0)
墙厚度 = 10

# Maze structure
maze_width = 30
maze_height = 20
maze = [[False for _ in range(maze_height)] for _ in range(maze_width)]
rocks = []
chest_positions = []

for i in range(maze_width):
    for j in range(maze_height):
        if random.random() < 0.3:  # 30% chance to have a rock
            rocks.append((i, j))
        if i == 5 and j == 10:  # Place chests
            chest_positions.append((i, j))

# Player movement variables
player_x = 15
player_y = 15
direction = (0, 0)

# Gold collection
gold = 0
chest_list = [(x, y) for x, y in chest_positions]

def draw_maze():
    global screen
    screen.fill(背景色)
    
    # Draw rocks
    for i, j in rocks:
        pygame.draw.rect(screen, (0, 0, 0), (i *墙厚度 + wall_thickness//2,
                                         j *墙厚度 + wall_thickness//2))
    
    # Draw walls
    wall_thickness = 5
    for i in range(maze_width):
        for j in range(maze_height):
            if maze[i][j]:
                pygame.draw.rect(screen, (0, 0, 0),
                               (i *墙厚度,
                                j *墙厚度 + wall_thickness//2,
                                宽度=墙厚度*2,
                                高度=(maze_height - j -1)*wall厚度)
    
    # Draw stalagmites
    for i in range(maze_width):
        for j in range(1, maze_height):
            if rocks and i == max([x for x, y in rocks if y <= j]):
                pygame.draw.line(screen, (0, 0, 0),
                               ((i *墙厚度 + wall_thickness//2), j*wall_thickness//2))
    
    # Draw chests
    for cx, cy in chest_list:
        pygame.draw.rect(screen, (200, 200, 0),
                        (cx *墙厚度 + wall_thickness//2,
                         cy *墙厚度 + wall_thickness//2,
                        宽度=wall厚度*2,
                        高度=wall厚度*2)
    
    # Draw player
    pygame.draw.rect(screen, (255, 0, 0),
                   (player_x *墙厚度 + wall_thickness//2,
                    player_y *墙厚度 + wall_thickness//2,
                   宽度=wall厚度*2,
                   高度=wall厚度*2)

def handle_keypresses():
    global direction
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        direction = (0, -1)
    elif keys[pygame.K_RIGHT]:
        direction = (0, 1)
    elif keys[pygame.K_UP]:
        direction = (-1, 0)
    elif keys[pygame.K_DOWN]:
        direction = (1, 0)

def update_player():
    global player_x, player_y
    new_x = player_x + direction[0]
    new_y = player_y + direction[1]
    
    # Check boundaries
    if new_x < 0 or new_x >= maze_width:
        return False
    if new_y < 0 or new_y >= maze_height:
        return False
    
    # Check for walls
    wall_found = False
    for i in range(maze_width):
        if not maze[i][new_y]:
            continue
        if (i *墙厚度 + wall_thickness//2 - direction[0]*wall厚度) == new_x*墙厚度 + wall_thickness//2:
            wall_found = True
            break
    if wall_found:
        return False
    
    player_x, player_y = new_x, new_y
    return True

def collect_chest():
    global gold, chest_list
    for i in range(len(chest_list)):
        cx, cy = chest_list[i]
        if cx == player_x and cy == player_y:
            gold += 10
            chest_list.pop(i)
            break

# Initialize display
screen = pygame.display.set_mode((屏幕宽,屏幕高))
pygame.display.set_caption("Cave Explorer")
clock = pygame.time.Clock()

running = True
while running:
    handle_keypresses()
    
    if update_player():
        pass
    
    draw_maze()
    collect_chest()
    
    # Display gold
    font = pygame.font.Font(None, 74)
    text = font.render(f'Gold: {gold}', True, (0, 0, 0))
    screen.blit(text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
