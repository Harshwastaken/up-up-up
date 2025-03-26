
# Import libraries
import pygame
import random
import os
from pygame import mixer
from spritesheet import SpriteSheet
from enemy import Enemy
from menu import GameMenu

# Initialize pygame
mixer.init()
pygame.init()

# Game window dimensions
SCREEN_WIDTH = 1260
SCREEN_HEIGHT = 720
S_SCREEN_WIDTH = 380

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Up Up Up')

# Set frame rate
clock = pygame.time.Clock()
FPS = 60

# Load music and sounds
pygame.mixer.music.load('assets1/music1.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0)
jump_fx = pygame.mixer.Sound('assets1/jump.mp3')
jump_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('assets1/death.mp3')
death_fx.set_volume(0.4)

# Game variables
SCROLL_THRESH = 200
GRAVITY = 0.5
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0
TARGET_FPS = 60
game_state = "menu"  # Possible states: menu, playing, game_over, paused

# Load high score
if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
else:
    high_score = 0

# Define colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PANEL = (107, 136, 254)

# Define font
font_small = pygame.font.SysFont('Lucida Sans', 26)
font_big = pygame.font.SysFont('Lucida Sans', 30)

# Load images
jumpy_image = pygame.image.load('assets1/jump.png').convert_alpha()
jumpy_jump = pygame.image.load('assets1/jimp3.png').convert_alpha()
bg_image = pygame.image.load('assets1/bg.png').convert_alpha()
platform_image = pygame.image.load('assets1/wood.png').convert_alpha()

# Bird spritesheet
bird_sheet_img = pygame.image.load('assets1/bird.png').convert_alpha()
bird_sheet = SpriteSheet(bird_sheet_img)

# Create the game menu
menu = GameMenu(SCREEN_WIDTH, SCREEN_HEIGHT)

# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function for drawing info panel
def draw_panel():
    pygame.draw.rect(screen, PANEL, (380, 0, 500, 30))
    pygame.draw.line(screen, WHITE, (S_SCREEN_WIDTH, 30), (880, 30), 2)
    draw_text('SCORE: ' + str(score), font_small, WHITE, 390, 0)

# Function for drawing the background
def draw_bg(bg_scroll):
    screen.blit(bg_image, (0, 0 + bg_scroll))
    screen.blit(bg_image, (0, -750 + bg_scroll))

def reset_game():
    
    global game_over, score, fade_counter, scroll, bg_scroll
    # Reset variables
    game_over = False
    score = 0 
    fade_counter = 0
    scroll = 0
    bg_scroll = 0
    # Reposition jumpy
    jumpy.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
    # Reset enemies
    enemy_group.empty()
    # Reset platforms
   # platform_group.empty() 
    # Create starting platform
    platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
    platform_group.add(platform)

  

# Player class
class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(jumpy_image, (60, 60))
        self.width = 60
        self.height = 60
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False
        self.acc = 1.5
        self.friction = -0.1

    def move(self):
        # Reset variables
        scroll = 0
        dx = 0
        dy = 0

        # Process keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_a] or key[pygame.K_LEFT]:
            dx = -5.5 * self.acc - self.friction
            self.flip = True
        if key[pygame.K_d] or key[pygame.K_RIGHT]:
            dx = 5.5 * self.acc + self.friction
            self.flip = False

        # Gravity
        self.vel_y += GRAVITY
        dy += self.vel_y + self.friction
  
        # Ensure player doesn't go off the edge of the screen
        if self.rect.left + dx < S_SCREEN_WIDTH:
            dx = S_SCREEN_WIDTH - self.rect.left
        if self.rect.right + dx > 880:
            dx = 880 - self.rect.right

        # Check collision with platforms
        for platform in platform_group:
            # Collision in the y direction
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Check if above the platform
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20
                        jump_fx.play()
                        
        # Check if the player has bounced to the top of the screen
        if self.rect.top <= SCROLL_THRESH:
            # If player is jumping
            if self.vel_y < 0:
                scroll = -dy
                self.image = pygame.transform.scale(jumpy_jump, (60, 60))
            else:
                self.image = pygame.transform.scale(jumpy_image, (60, 60))
                
        # Update rectangle position
        self.rect.x += dx
        self.rect.y += dy + scroll

        # Update mask
        self.mask = pygame.mask.from_surface(self.image)

        return scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 16))
        self.moving = moving
        self.move_counter = random.randint(0, 40)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        # Moving platform side to side if it is a moving platform
        if self.moving == True:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed

        # Change platform direction if it has moved fully or hit a wall
        if self.move_counter >= 100 or self.rect.left < S_SCREEN_WIDTH or self.rect.right > 880:
            self.direction *= -1
            self.move_counter = 0

        # Update platform's vertical position
        self.rect.y += scroll

        # Check if platform has gone off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Create player instance
jumpy = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

# Create sprite groups
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# Create starting platform
platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
platform_group.add(platform)

# Game loop
run = True
while run:
    clock.tick(FPS)
    
    # Handle events first
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            # Update high score before quitting
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "playing":
                    # Pause the game
                    game_state = "menu"
                    menu.game_paused = True
                elif game_state == "menu" and menu.game_paused:
                    # Resume the game
                    game_state = "playing"
    
    # Game state machine
    if game_state == "menu":
        # Draw the game screen underneath if paused
        if menu.game_paused:
            draw_bg(bg_scroll)
            platform_group.draw(screen)
            enemy_group.draw(screen)
            jumpy.draw()
            draw_panel()
        else:
            # Just draw background if not paused
            draw_bg(0)
        
        # Update and draw menu
        menu_action = menu.update(events)
        menu.draw(screen)
        
        # Handle menu actions
        if menu_action == "play":
            if menu.game_paused:
                # Resume game
                game_state = "playing"
                menu.game_paused = False
            else:
                # Start new game
                reset_game()
                game_state = "playing"
        elif menu_action == "exit":
            # Update high score before quitting
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            run = False
    
    elif game_state == "playing":
        # Draw background
        draw_bg(bg_scroll)
        
        if not game_over:
            # Get player movement
            scroll = jumpy.move()

            # Generate platforms
            if len(platform_group) < MAX_PLATFORMS:
                p_w = random.randint(60, 100) 
                p_x = random.randint(S_SCREEN_WIDTH, 880 - p_w)
                p_y = platform.rect.y - random.randint(80, 120)
                p_type = random.randint(1, 2)
                if p_type == 1 and score > 500:
                    p_moving = True
                else:
                    p_moving = False
                platform = Platform(p_x, p_y, p_w, p_moving)
                platform_group.add(platform)

            # Update platforms
            platform_group.update(scroll)

            # Generate enemies
            if len(enemy_group) == 0 and score > 1700:
                enemy = Enemy(SCREEN_WIDTH, 100, bird_sheet, 1.5)
                enemy_group.add(enemy)

            # Update enemies
            enemy_group.update(scroll, SCREEN_WIDTH)

            # Update score
            if scroll > 0:
                score += int(scroll)
                FPS+=.00001

            # Draw line at previous high score
            pygame.draw.line(screen, WHITE, (S_SCREEN_WIDTH, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
            draw_text('HIGH SCORE', font_small, WHITE, S_SCREEN_WIDTH, score - high_score + SCROLL_THRESH)

            # Update background scroll
            bg_scroll += scroll

            # Reset background scroll
            if bg_scroll >= 750:
                bg_scroll = 0

            # Draw sprites
            platform_group.draw(screen)
            enemy_group.draw(screen)
            jumpy.draw()

            # Draw panel
            draw_panel()

            # Check game over
            if jumpy.rect.top > SCREEN_HEIGHT:
                game_over = True
                death_fx.play()
                
            # Check for collision with enemies
            if pygame.sprite.spritecollide(jumpy, enemy_group, False):
                if pygame.sprite.spritecollide(jumpy, enemy_group, False, pygame.sprite.collide_mask):
                    game_over = True
                    death_fx.play()
        
        else:  # Game over state
            if fade_counter < SCREEN_WIDTH:
                fade_counter += 10
                for y in range(0, 16, 2):
                    pygame.draw.rect(screen, BLACK, (0, y * 100, fade_counter, 100))
                    pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - fade_counter, (y + 1) * 100, SCREEN_WIDTH, 100))
            else:
                game_state = "game_over"
                
    elif game_state == "game_over":
        # Draw game over screen
        draw_text('GAME OVER!', font_big, BLACK, SCREEN_WIDTH // 2 - 100, 300)
        draw_text('SCORE: ' + str(score), font_big, BLACK, SCREEN_WIDTH // 2 - 100, 350)
        draw_text('PRESS SPACE TO PLAY AGAIN', font_big, BLACK, SCREEN_WIDTH // 2 - 200, 400)
        draw_text('PRESS ESC FOR MENU', font_big, BLACK, SCREEN_WIDTH // 2 - 150, 450)
        
        # Update high score
        if score > high_score:
            high_score = score
            with open('score.txt', 'w') as file:
                file.write(str(high_score))
            # Update menu high score
            menu.high_score = high_score
            menu.load_high_score()
        
        # Check for key presses
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            # Reset the game and start playing
            reset_game()
            game_over = False
            game_state = "playing"
        elif key[pygame.K_ESCAPE]:
            # Go to menu
            menu.game_paused = False  # Not paused, new game
            game_state = "menu"

    # Update display window
    pygame.display.update()

pygame.quit()