# pygame tutorial https://www.youtube.com/watch?v=Q-__8Xw9KTM&t=254s
import pygame
import os
import time
import random
from pygame import mixer
pygame.font.init()

WIDTH, HEIGHT = 850, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Defender")

# Load sounds
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()

explosion_fx = pygame.mixer.Sound("assets/explosion.wav")
explosion_fx.set_volume(.1)

laser_fx = pygame.mixer.Sound("assets/laser.mp3")
laser_fx.set_volume(.1)

background_fx = pygame.mixer.Sound("assets/background.mp3")
background_fx.set_volume(.1)

opening_fx = pygame.mixer.Sound("assets/opening.mp3")
opening_fx.set_volume(.1)

next_level_fx = pygame.mixer.Sound("assets/next_level.mp3")
next_level_fx.set_volume(.1)

game_over_fx = pygame.mixer.Sound("assets/game_over.wav")
game_over_fx.set_volume(.1)

loss_life_fx = pygame.mixer.Sound("assets/loss_life.wav")
loss_life_fx.set_volume(.1)

healing_health_fx = pygame.mixer.Sound("assets/healing_health.wav")
healing_health_fx.set_volume(.1)

buff_triple_fx = pygame.mixer.Sound("assets/buff_triple.wav")
buff_triple_fx.set_volume(.1)

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue.png"))
PURPLE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_purple.png"))
ORANGE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_orange.png"))

HEALING_RED = pygame.image.load(os.path.join("assets", "pixel_healing_red.png"))
BUFF_TRIPLE = pygame.image.load(os.path.join("assets", "pixel_buff_triple.png"))


# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_main.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
PURPLE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_purple.png"))
ORANGE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_orange.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_main.png"))
YELLOW_LASER_TRIPLE = pygame.image.load(os.path.join("assets", "pixel_laser_main_triple.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img 
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height): # if laser if off screen
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship: # give attributes to objects
    COOLDOWN = 30 # half a second as fps is 60
    def __init__(self, x, y, health=100): 
        self.x = x
        self.y = y
        self.health = health
        self.player_img = None
        self.laser_img = None
        self.lasers = [] # equals blank
        self.cool_down_counter = 0

    def draw(self, window): # draw lasers
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
    
    def move_lasers(self, vel, obj): # moving lasers 
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10 # damage
                self.lasers.remove(laser)
                explosion_fx.play() # player getting hit


    def cooldown(self): # not shooting too fast
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1 

    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()
    

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) # where pixels are when collision
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            explosion_fx.play() # enemy getting hit by laser
    
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
                "purple": (PURPLE_SPACE_SHIP, PURPLE_LASER),
                "orange": (ORANGE_SPACE_SHIP, ORANGE_LASER)
                } # assigning color based on ship color

    def __init__(self, x, y, color, health=100): 
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1 

class Healing:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.healing_img = HEALING_RED
        self.mask = pygame.mask.from_surface(self.healing_img)

    def draw(self, window): # draw healing
        window.blit(self.healing_img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def get_width(self):
        return self.healing_img.get_width()
    def get_height(self):
        return self.healing_img.get_height()

class Buff:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.buff_img = BUFF_TRIPLE
        self.mask = pygame.mask.from_surface(self.buff_img)
    
    def draw(self, window):
        window.blit(self.buff_img, (self.x, self.y))

    def move(self, vel):
        self.y += vel
    
    def get_width(self):
        return self.buff_img.get_width()
    def get_height(self):
        return self.buff_img.get_height()


def collide(obj1, obj2): # Overlapping
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
    
def main():
    run = True
    FPS = 60 
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    healings = []
    buffs = []
    wave_length_enemy = 5
    wave_length_healing = 1
    wave_length_buff = 1
    enemy_vel = 1
    player_vel = 5 # how fast to move in every direction (pixels)
    enemy_laser_vel = 5 # laser speed
    player_laser_vel = 7
    healing_vel = 1
    buff_vel = 1

    player= Player(330, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0


    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw test
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)
        
        for healing in healings:
            healing.draw(WIN)

        for buff in buffs:
            buff.draw(WIN)
    
        player.draw(WIN)

        if lost: 
            lost_label = lost_font.render("You Lost!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350)) # centering label math

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost: # when lost goes to 3 sec timer and quits the game
            game_over_fx.play() 
            if lost_count > FPS * 2: 
                run = False
            else: 
                continue

        if len(enemies) == 0: # when enemies of the screen
            level += 1
            wave_length_enemy += 5 # add more enemies 
            next_level_fx.play() # complete next stage
            for i in range(wave_length_enemy):
                enemy = Enemy(random.randrange(100, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green", 
                "purple", "orange"]))
                enemies.append(enemy)
            
        if len(healings) == 0: # when healing of the screen
            wave_length_healing += 1 # add more healing
            for i in range(wave_length_healing):
                healing = Healing(random.randrange(100, WIDTH-100), random.randrange(-1500,-100), random.choice(["HEALING_RED"]))
                healings.append(healing)

        if len(buffs) == 0: 
            wave_length_buff 
            for i in range(wave_length_buff):
                buff = Buff(random.randrange(100, WIDTH-100), random.randrange(-1500,-100), random.choice(["BUFF_TRIPLE"]))
                buffs.append(buff)
    

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel # moving up because staring position is top left
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 20 < HEIGHT: # down
            player.y += player_vel 
        if keys[pygame.K_SPACE]:
            player.shoot()
            laser_fx.play() # player shoot laser

        for enemy in enemies[:]: # copy
            enemy.move(enemy_vel)
            enemy.move_lasers(enemy_laser_vel, player)
            
            if random.randrange(0, 2*60) == 1: # probability of enemy shooting
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                explosion_fx.play() # player collide with enemy
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
                loss_life_fx.play() # loss life from enemy passing

        for healing in healings[:]:
            healing.move(healing_vel)

            if collide(healing, player):
                player.health += 5
                if player.health >= 100: # health cap
                    player.health = 100
                healings.remove(healing)
                healing_health_fx.play() # player collide with healing
                
            elif healing.y + healing.get_height() > HEIGHT:
                healings.remove(healing)
        
        for buff in buffs[:]:
            buff.move(buff_vel)

            if collide(buff, player):
                player.laser_img = YELLOW_LASER_TRIPLE
                buffs.remove(buff)
                buff_triple_fx.play()


        player.move_lasers(-player_laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    opening_fx.play() # opening 
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    

    pygame.quit()


main_menu()

