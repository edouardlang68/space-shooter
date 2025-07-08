import pygame
from random import randint, uniform

from os.path import join 

GAME_STATE_PLAYING = 0
GAME_STATE_GAME_OVER = 1
current_game_state = GAME_STATE_PLAYING

WINDOW_WIDTH, WINDOW_HEIGHT = 1100, 750

player_score = 0

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load('space shooter/images/spaceship.png')
        self.rect = self.image.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 200


        # mask
        self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        if keys[pygame.K_SPACE] and self.can_shoot :
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks() 
            laser_sound.play()
 
        self.laser_timer()


class Star(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))
  
class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom = pos)

        self.mask = pygame.mask.from_surface(self.image)


    
    def update(self, dt) :
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite) :

    def __init__(self, surf, pos, groups) :
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_rect(center =pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(400, 500)
        self.rotation_speed = randint(50, 90)
        self.rotation = 0

        self.mask = pygame.mask.from_surface(self.image)


    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime :
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_rect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        explosion_sound.play()

    
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index) % len(self.frames)]
        else : 
            self.kill()

def collisions():
    # --- FIX: Added player_score to the global declaration ---
    global running, current_game_state, player_score

    # Collision between player and meteor
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        current_game_state = GAME_STATE_GAME_OVER
        AnimatedExplosion(explosion_frames, player.rect.center, all_sprites)
        damage_sound.play()
        player.kill() # Remove the player sprite after collision

    # Collision between laser and meteor
    for laser in laser_sprites:
        collided_meteors = pygame.sprite.spritecollide(laser, meteor_sprites, True, pygame.sprite.collide_mask)
        if collided_meteors :
            laser.kill()
            for meteor in collided_meteors:
                AnimatedExplosion(explosion_frames, meteor.rect.center, all_sprites)
                player_score += 10 # This will now correctly modify the global player_score

def display_score():

    global player_score
    text_surf = font.render(str(player_score), True, (240,240,240))
    text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(18,15).move(0, -3), 5, 10)

def display_game_over_screen():
    global player_score    
    display_surface.fill((30, 0, 40)) 

    # Texte "Game Over"
    game_over_font = pygame.font.Font(join('space shooter', 'images', 'Oxanium-Bold.ttf'), 80)
    game_over_surf = game_over_font.render('GAME OVER', True, (255, 255, 255))
    game_over_rect = game_over_surf.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 100))
    display_surface.blit(game_over_surf, game_over_rect)

    final_score_value = player_score


    score_font = pygame.font.Font(join('space shooter', 'images', 'Oxanium-Bold.ttf'), 50)
    score_surf = score_font.render(f'Score final: {final_score_value}', True, (240, 240, 240))
    score_rect = score_surf.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    display_surface.blit(score_surf, score_rect)


    # Instruction pour rejouer
    restart_font = pygame.font.Font(join('space shooter', 'images', 'Oxanium-Bold.ttf'), 30)
    restart_surf = restart_font.render('Appuyez sur ESPACE pour rejouer ou ECHAP pour quitter', True, (200, 200, 200))
    restart_rect = restart_surf.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 100))
    display_surface.blit(restart_surf, restart_rect)




# general setup
pygame.init()

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('space shooter')
running = True
clock = pygame.time.Clock()

# import
star_surf = pygame.image.load('space shooter/images/star.png')
meteor_surf = pygame.image.load('space shooter/images/meteor.png')
laser_surf = pygame.image.load('space shooter/images/laser.png')
font = pygame.font.Font(join('space shooter', 'images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('space shooter', 'images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
laser_sound = pygame.mixer.Sound(join('space shooter', 'audio', 'laser.wav'))
explosion_sound = pygame.mixer.Sound(join('space shooter', 'audio', 'explosion.wav'))
damage_sound = pygame.mixer.Sound(join('space shooter', 'audio', 'damage.ogg'))
game_music = pygame.mixer.Sound(join('space shooter', 'audio', 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops = -1)


 #sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(star_surf, (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)), all_sprites)
player = Player(all_sprites)


# meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

test_rect = pygame.Rect(0, 0, 300, 600)

while running :
    dt = clock.tick() / 1000
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT :
            running = False
        if current_game_state == GAME_STATE_PLAYING:
            if event.type == meteor_event:
                x,y = randint(0, WINDOW_WIDTH), randint(-200, -100)
                Meteor(meteor_surf, (x,y), (all_sprites, meteor_sprites))
        elif current_game_state == GAME_STATE_GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:

                    all_sprites.empty()
                    meteor_sprites.empty()
                    laser_sprites.empty()

                    # Réinitialiser le joueur et les étoiles
                    for i in range(20):
                        Star(star_surf, (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)), all_sprites)
                    player_score = 0
                    player = Player(all_sprites)

                    # Réinitialiser le timer des météores si nécessaire
                    pygame.time.set_timer(meteor_event, 500) # Relance le timer

                    current_game_state = GAME_STATE_PLAYING # Retourne à l'état de jeu
                elif event.key == pygame.K_ESCAPE:
                    running = False # Quitter le jeu depuis l'écran de fin

    if current_game_state == GAME_STATE_PLAYING:
        all_sprites.update(dt)
        collisions()

        display_surface.fill('#3a2e3f')
        display_score() 
        all_sprites.draw(display_surface)

    elif current_game_state == GAME_STATE_GAME_OVER:
        display_game_over_screen()

    pygame.display.update()

pygame.quit()