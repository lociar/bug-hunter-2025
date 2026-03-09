"""Built using guide from https://dev.to/lovelacecoding/how-to-build-your-first-python-game-a-step-by-step-guide-to-creating-a-simple-shooter-with-pygame-f0k"""

import pygame
import sys
import random
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this when running from .exe
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


#initialise PyGame
pygame.init()

#set up game window
screen_width = 1000
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
background_img = pygame.image.load(resource_path("assets/background.jpg")).convert_alpha()
background_img = pygame.transform.scale(background_img, (screen_width, screen_height))
start_background_img = pygame.image.load(resource_path("assets/start_background.jpg")).convert_alpha()
start_background_img = pygame.transform.scale(start_background_img, (screen_width, screen_height))
gameover_background_img = pygame.image.load(resource_path("assets/gameover_background.jpg")).convert_alpha()
gameover_background_img = pygame.transform.scale(gameover_background_img, (screen_width, screen_height))
pygame.display.set_caption("Simple Shooter Game")

#player settings
player_img = pygame.image.load(resource_path("assets/pipe.png")).convert_alpha()
player_width = 100
player_height = 100
player_x = screen_width // 2 - player_width //2
player_y = screen_height - player_height
player_img = pygame.transform.scale(player_img, (player_width, player_height))
player_speed = 9
player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

#bullet settings
bullet_img = pygame.image.load(resource_path("assets/bullet.png")).convert_alpha()
bullet_width = 70
bullet_height = 70
bullet_img = pygame.transform.scale(bullet_img, (bullet_width, bullet_height))
bullet_speed = 12
bullets = []

#score tracker
score = 0
high_score = 0
lives = 3

#enemy settings
enemy_img = pygame.image.load(resource_path("assets/enemy.png")).convert_alpha()
enemy_width = 80
enemy_height = 80
enemy_img = pygame.transform.scale(enemy_img, (enemy_width, enemy_height))
enemy_base_speed = 1.5
enemies = []

#spawn enemy every 2 seconds
enemy_timer = 0
enemy_spawn_time = 1800

#initialise font
score_font = pygame.font.Font(resource_path("assets/pixel_font.ttf"), 32)
game_over_font = pygame.font.Font(resource_path("assets/pixel_font.ttf"), 62)

#set game state
show_title = True
game_over = False

#explosion image
explosion_img = pygame.image.load(resource_path("assets/explosion.png")).convert_alpha()
explosion_img = pygame.transform.scale(explosion_img, (enemy_width, enemy_height))

#sound effects
shoot_sound = pygame.mixer.Sound(resource_path("assets/shoot.mp3"))
hit_sound = pygame.mixer.Sound(resource_path("assets/hit.mp3"))
game_over_sound = pygame.mixer.Sound(resource_path("assets/game_over.mp3"))
enemy_escape_sound = pygame.mixer.Sound(resource_path("assets/enemy_escape.mp3"))

#collision detection function
def check_collision(rect1, rect2):
     return rect1.colliderect(rect2)

#set frame rate
clock = pygame.time.Clock()

#Play music
pygame.mixer.music.load(resource_path("assets/music.mp3"))
pygame.mixer.music.set_volume(0.3) #set at 30% volume
pygame.mixer.music.play(-1) #loop indefinitely

#main game loop
while True:
    #when game not yet over
    if show_title:
        #Draw background and Title Text
                #fill screen with background image
        screen.blit(start_background_img, (0,0))

        #display title and start message
        title_text = game_over_font.render(f"Bug Hunter 2025", True, (255, 100, 200))
        start_text = score_font.render("Hit 'S' to start", True, (100, 255, 200))
        controls_text1 = score_font.render("Space [===] to shoot", True, (255, 100, 200))
        controls_text2 = score_font.render("Arrow keys <= => to move", True, (255, 100, 200))
        screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, screen_height//2 - 80))
        screen.blit(start_text, (screen_width//2 - start_text.get_width()//2, screen_height//2))
        screen.blit(controls_text1, (screen_width//2 - controls_text1.get_width()//2, screen_height//2 + 80))
        screen.blit(controls_text2, (screen_width//2 - controls_text2.get_width()//2, screen_height//2 + 120))
        
        pygame.display.flip()

        #event processing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    show_title = False
                    game_over = False

    elif not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    #Create a bullet at current player position
                    bullet_x = player_x + player_width // 2 - bullet_width // 2
                    bullet_y = player_y
                    bullets.append(pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height))
                    #create sound effect
                    shoot_sound.play()

        #handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed
        player_rect.update(player_x, player_y, player_width, player_height)

        #update bullet positions
        for bullet in bullets:
            bullet.y -= bullet_speed

        #update enemy positions and spawn new ones
        current_time = pygame.time.get_ticks()
        if current_time - enemy_timer > enemy_spawn_time:
            enemy_x = random.randint(0, screen_width - enemy_width)
            enemy_y = -enemy_height
            enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)
            enemy_speed = min(enemy_base_speed + (score*0.05), player_speed)
            enemies.append([enemy_rect, enemy_speed, "enemy", None]) #list: (rect, speed)
            enemy_timer = current_time

            #gradually increase spawn rate
            enemy_spawn_time = max(700, 2000 - (score * 30) + random.randint(-100, 100))

        #updating enemy positions
        for enemy in enemies:
            enemy[0].y += enemy[1] #enemy[0] = rect, enemy[1] = speed

        #check for bullet-enemy collisions, on collision remove bullet and enemy and +1 to score
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if check_collision(bullet, enemy[0]): #use enemy[0]
                    hit_sound.play()
                    bullets.remove(bullet)
                    enemy[2] = "explosion"
                    enemy[3] = pygame.time.get_ticks() #start explosion timer
                    score +=1
                    break

        #game over if enemies off-screen
        for enemy in enemies[:]:
            if enemy[0].y > screen_height:
                enemies.remove(enemy)
                enemy_escape_sound.play()
                lives -=1
                if lives == 0:
                    game_over_sound.play()
                    game_over = True
                    break
        

        #remove off-screen bullets
        bullets = [bullet for bullet in bullets if bullet.y > 0]

        #fill screen with background image
        screen.blit(background_img, (0,0))

        #set high score
        if score > high_score:
            high_score = score

        #display score on screen
        text_score = score_font.render(f"Score: {score}", True, (180, 200, 255))
        screen.blit(text_score, (10, 10))

        #display lives on screen
        text_lives = score_font.render(f"Lives: {lives}", True, (180, 200, 255))
        screen.blit(text_lives, (10, 60))

        #display high score if >0
        if high_score > 0:
            high_score_text = score_font.render(f"High Score: {high_score}", True, (180, 200, 255))
            screen.blit(high_score_text, (10, 110))
    

        #draw player
        screen.blit(player_img, player_rect)

        #draw bullets
        for bullet in bullets:
            screen.blit(bullet_img, bullet)

        #draw enemies
        for enemy in enemies:
            if enemy[2] == "explosion":
                screen.blit(explosion_img, enemy[0])
                if pygame.time.get_ticks() - enemy[3] > 200: #200ms
                    enemies.remove(enemy)
            else:
                screen.blit(enemy_img, enemy[0])

        #update display
        pygame.display.flip()

        #cap frame rate at 60fps
        clock.tick(60)
    
    #when game_over is true
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN: #Hit R to restart
                if event.key == pygame.K_r:
                    #reset game state
                    bullets.clear()
                    enemies.clear()
                    score = 0
                    lives = 3
                    player_x = screen_width // 2 - player_width // 2
                    player_y = screen_height - player_height
                    player_rect.update(player_x, player_y, player_width, player_height)
                    game_over = False
                    enemy_timer = pygame.time.get_ticks()
                    enemy_spawn_time = 2000  # Reset spawn time

        #fill screen with background image
        screen.blit(gameover_background_img, (0,0))

        
        #display score on screen
        game_over_text = game_over_font.render(f"GAME OVER!", True, (255, 200, 220))
        final_score_text = game_over_font.render(f"Final Score: {score}", True, (255, 200, 220))
        restart_text = score_font.render("Hit 'R' to restart", True, (255, 0, 0))
        screen.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, screen_height//2 - 80))
        screen.blit(final_score_text, (screen_width//2 - final_score_text.get_width()//2, screen_height//2))
        screen.blit(restart_text, ((screen_width//2 - final_score_text.get_width()//2) + 120, screen_height//2 + 90))

        #update high score if appropriate
        if score > high_score:
            high_score = score

        #update display
        pygame.display.flip()

