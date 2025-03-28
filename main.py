import pygame
import random
import sys
import time
import arabic_reshaper
from bidi.algorithm import get_display
import os
import json

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LEVEL_COLORS = [WHITE, (200, 200, 200), (150, 150, 150), (100, 100, 100), BLACK]  # ألوان المستويات

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("الفوز للقوي - معمول بواسطة محمود")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load assets
player_image = pygame.image.load("player_with_gun.png")  # صورة اللاعب
player_image = pygame.transform.scale(player_image, (50, 50))

enemy_image = pygame.image.load("mutant_chicken.png")  # صورة الفراخ المتحولة
enemy_image = pygame.transform.scale(enemy_image, (50, 50))

# Player properties
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_speed = 5
player_level = 1  # مستوى اللاعب
kills_for_next_level = random.randint(5, 10)  # عدد القتلى المطلوب للانتقال إلى المستوى التالي

# Obstacle properties
obstacle_width = 50
obstacle_height = 50
obstacle_speed = 3
obstacles = []

# Bullet properties
bullets = []
bullet_width = 5
bullet_height = 10
bullet_speed = 7

# Enemy bullet properties
enemy_bullets = []
enemy_bullet_width = 5
enemy_bullet_height = 10
enemy_bullet_speed = 3

# Game state
is_game_over = False
score = 0
kills = 0  # عدد القتلى
start_time = time.time()  # لتتبع الوقت
is_firing = False  # حالة إطلاق النار
level = 1  # المستوى الحالي
highest_score = 0  # أعلى سكور
highest_kills = 0  # أعلى عدد قتلى
control_mode = "keyboard"  # وضع التحكم الافتراضي

# Font for game over text, score, and time
font = pygame.font.Font(None, 60)
score_font = pygame.font.Font(None, 28)

# Save and load player level
SAVE_FILE = "player_data.json"

def save_player_data():
    data = {
        "highest_score": highest_score,
        "highest_kills": highest_kills,
        "player_level": player_level
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_player_data():
    global highest_score, highest_kills, player_level
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            highest_score = data.get("highest_score", 0)
            highest_kills = data.get("highest_kills", 0)
            player_level = data.get("player_level", 1)

# Load saved data
load_player_data()

# Function to reset the game
def reset_game():
    global player_x, player_y, obstacles, bullets, enemy_bullets, is_game_over, score, kills, obstacle_speed, start_time, level, player_level, kills_for_next_level
    player_x = WIDTH // 2
    player_y = HEIGHT - 100
    obstacles = []
    bullets = []
    enemy_bullets = []
    is_game_over = False
    score = 0
    kills = 0
    obstacle_speed = 3
    start_time = time.time()
    level = 1
    kills_for_next_level = random.randint(5, 10)

# Function to generate obstacles
def generate_obstacle():
    x = random.randint(0, WIDTH - obstacle_width)
    y = -obstacle_height
    obstacles.append([x, y])

# Function to update obstacles
def update_obstacles():
    global is_game_over, score, obstacle_speed
    for obstacle in obstacles[:]:
        obstacle[1] += obstacle_speed
        if obstacle[1] > HEIGHT:
            obstacles.remove(obstacle)
        # Check collision
        if (
            player_x < obstacle[0] + obstacle_width and
            player_x + player_size > obstacle[0] and
            player_y < obstacle[1] + obstacle_height and
            player_y + player_size > obstacle[1]
        ):
            is_game_over = True

# Function to draw obstacles
def draw_obstacles():
    for obstacle in obstacles:
        screen.blit(enemy_image, (obstacle[0], obstacle[1]))

# Function to update bullets
def update_bullets():
    global score, kills, player_level, kills_for_next_level
    for bullet in bullets[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullets.remove(bullet)
        else:
            for obstacle in obstacles[:]:
                if (
                    bullet[0] < obstacle[0] + obstacle_width and
                    bullet[0] + bullet_width > obstacle[0] and
                    bullet[1] < obstacle[1] + obstacle_height and
                    bullet[1] + bullet_height > obstacle[1]
                ):
                    obstacles.remove(obstacle)
                    bullets.remove(bullet)
                    score += 10
                    kills += 1
                    # Check if player levels up
                    if kills >= kills_for_next_level:
                        player_level += 1
                        kills_for_next_level += random.randint(5, 10)
                    break

# Function to update enemy bullets
def update_enemy_bullets():
    global is_game_over
    for bullet in enemy_bullets[:]:
        bullet[1] += enemy_bullet_speed
        if bullet[1] > HEIGHT:
            enemy_bullets.remove(bullet)
        elif (
            player_x < bullet[0] + enemy_bullet_width and
            player_x + player_size > bullet[0] and
            player_y < bullet[1] + enemy_bullet_height and
            player_y + player_size > bullet[1]
        ):
            is_game_over = True

# Function to draw bullets
def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(screen, BLACK, (bullet[0], bullet[1], bullet_width, bullet_height))

# Function to draw enemy bullets
def draw_enemy_bullets():
    for bullet in enemy_bullets:
        pygame.draw.rect(screen, RED, (bullet[0], bullet[1], enemy_bullet_width, enemy_bullet_height))

# Game loop
running = True
while running:
    # Change background color based on level
    screen.fill(LEVEL_COLORS[min(level - 1, len(LEVEL_COLORS) - 1)])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_player_data()
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not is_game_over:
                is_firing = True  # بدء إطلاق النار
            if event.key == pygame.K_r and is_game_over:
                if score > highest_score:
                    highest_score = score
                if kills > highest_kills:
                    highest_kills = kills
                save_player_data()
                reset_game()
            if event.key == pygame.K_c:  # تبديل وضع التحكم
                control_mode = "touch" if control_mode == "keyboard" else "keyboard"
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                is_firing = False  # إيقاف إطلاق النار

    if is_game_over:
        game_over_text = font.render("Game Over!", True, BLACK)
        restart_text = score_font.render("Press R to Restart", True, BLACK)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height()))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.flip()
        continue

    # Get keys pressed
    keys = pygame.key.get_pressed()
    if control_mode == "keyboard":
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player_y > 0:
            player_y -= player_speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player_y < HEIGHT - player_size:
            player_y += player_speed
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_x > 0:
            player_x -= player_speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_x < WIDTH - player_size:
            player_x += player_speed

    # Fire bullets continuously if space is held
    if is_firing and not is_game_over:
        bullets.append([player_x + player_size // 2 - bullet_width // 2, player_y])

    # Generate enemy bullets periodically
    for obstacle in obstacles:
        if random.randint(1, 100) == 1:  # إطلاق نار بطيء
            enemy_bullets.append([obstacle[0] + obstacle_width // 2, obstacle[1] + obstacle_height])

    # Update and draw obstacles
    update_obstacles()
    draw_obstacles()

    # Update and draw bullets
    update_bullets()
    draw_bullets()

    # Update and draw enemy bullets
    update_enemy_bullets()
    draw_enemy_bullets()

    # Draw player
    screen.blit(player_image, (player_x, player_y))

    # Generate obstacles periodically
    if random.randint(1, 30) == 1:
        generate_obstacle()

    # Increase score over time
    score += 1

    # Increase obstacle speed and level over time
    if score % 100 == 0:
        obstacle_speed += 0.1
        if score % 500 == 0:
            level += 1

    # Draw score
    score_text = score_font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # Draw kills
    kills_text = score_font.render(f"Kills: {kills}", True, BLACK)
    screen.blit(kills_text, (10, 40))

    # Draw player level
    level_text = score_font.render(f"Player Level: {player_level}", True, BLACK)
    screen.blit(level_text, (10, 70))

    # Draw elapsed time in minutes and seconds
    elapsed_time = int(time.time() - start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    time_text = score_font.render(f"Time: {minutes}m {seconds}s", True, BLACK)
    screen.blit(time_text, (10, 100))

    # Draw highest score and kills
    high_score_text = score_font.render(f"High Score: {highest_score}", True, BLACK)
    high_kills_text = score_font.render(f"High Kills: {highest_kills}", True, BLACK)
    screen.blit(high_score_text, (10, 130))
    screen.blit(high_kills_text, (10, 160))

    # Draw credits (Arabic text reshaped)
    reshaped_text = arabic_reshaper.reshape("by Mahmoud")
    bidi_text = get_display(reshaped_text)
    credits_text = score_font.render(bidi_text, True, BLACK)
    screen.blit(credits_text, (10, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
