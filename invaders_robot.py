import pygame
from pygame import mixer
from pygame.locals import *
import random
# bắt đầu khởi tạo trò chơi
pygame.init()
mixer.init()


# tạo cửa sổ game
screen_width = 1000
screen_height = 600
screen = pygame.display.set_mode((screen_width,screen_height))


# tên game và avatar game
title = pygame.display.set_caption("Invaders Robot")
icon = pygame.image.load(r'C:\Python Game\Game\icon_set.png')
pygame.display.set_icon(icon)


# thay đổi background
background = pygame.image.load(r'C:\Python Game\Game\bg.png')
background_menu = pygame.image.load(r'C:\Python Game\Game\background3i.png')
logo_ueh = pygame.image.load(r'C:\Python Game\Game\logo_ueh.png')


# thêm âm thanh
laser_fx = pygame.mixer.Sound(r'C:\Python Game\Game\laser.wav')
laser_fx.set_volume(0.1)

background_fx = pygame.mixer.Sound(r'C:\Python Game\Game\background.wav')
background_fx.set_volume(0.25)



# thêm player
playerImg = pygame.image.load(r'C:\Python Game\Game\spaceship.png')


# thêm robot kẻ địch
robot1 = pygame.image.load(r'C:\Python Game\Game\robot1.png')
robot1 = pygame.transform.scale(robot1, (65, 60))

robot2 = pygame.image.load(r'C:\Python Game\Game\robot2.png')
robot2 = pygame.transform.scale(robot2, (70, 70))

robot3 = pygame.image.load(r'C:\Python Game\Game\robot3.png')
robot4 = pygame.image.load(r'C:\Python Game\Game\robot4.png')


# thêm bullet của player và kẻ địch
player_bullet = pygame.image.load(r'C:\Python Game\Game\bullet.png')
robot_bullet = pygame.image.load(r'C:\Python Game\Game\robot_bullet.png')


# collide
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


# Tạo lớp Bullet
class Bullet:
    def __init__(self, x, y, img):
        self.x = x + 30
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


# Tạo lớp Ship
class Ship:
    COOLDOWN = 15
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.bullets = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    def move_bullets(self, vel, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(screen_height):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                obj.health -= 10
                self.bullets.remove(bullet)
    def shoot(self):
        if self.cool_down_counter == 0:
            bullet = Bullet(self.x, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1
            laser_fx.play()

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


# Tạo lớp Player
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = playerImg
        self.bullet_img = player_bullet
        self.mask =pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_bullets(self, vel, objs):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(screen_height):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        objs.remove(obj)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    


# Tạo lớp Robot kẻ địch
class Enemy(Ship):
    ROBOT_MAP = {
                "Robot1": (robot1, robot_bullet),
                "Robot2": (robot2, robot_bullet),
                "Robot3": (robot3, robot_bullet),
                "Robot4": (robot4, robot_bullet)
                }
    def __init__(self, x, y, robot, health = 100):
        super().__init__(x, y, health)
        self.ship_img, self.bullet_img = self.ROBOT_MAP[robot]
        self.mask =  pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel
    
    def shoot(self):
        if self.cool_down_counter == 0:
            bullet = Bullet(self.x-20, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1


def main():

    run = True
    fps = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 8
    bullet_vel = 5

    player = Player(500, 500)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    background_fx.play(-1)
    def redraw_window():
        #thêm background và logo
        screen.blit(background, (0,0))
        screen.blit(logo_ueh, (0,0))

        # hiện chữ lên màn hình
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        screen.blit(lives_label, (800, 00))
        screen.blit(level_label, (10, 75))

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)

        if lost:
            lost_label = lost_font.render("GAME OVER!!", 1, (255,255,255))
            screen.blit(lost_label, (screen_width/2 - lost_label.get_width()/2, 350))

        pygame.display.update()
    while run:
        clock.tick(fps)
        redraw_window()
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > fps * 3:
                run = False
            else:
                continue
        
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, screen_width-100), random.randrange(-1500, -100), random.choice(["Robot1", "Robot2", "Robot3","Robot4"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


        # chuyển động của player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < screen_width: # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < screen_height: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_F1]:
            background_fx.stop()
        if keys[pygame.K_F2]:
            background_fx.play()


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_bullets(bullet_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > screen_height:
                lives -= 1
                enemies.remove(enemy)

        player.move_bullets(-bullet_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("Times New Roman", 60)
    run = True
    blink_timer = 0
    background_fx.play(-1)
    while run:
        screen.blit(background_menu, (0,0))
        #làm hiệu ứng nhấp nháy cho dòng chữ
        if blink_timer < 30:
            title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
            screen.blit(title_label, (screen_width/2 - title_label.get_width()/2, 500))
        elif blink_timer < 60:
            pass
        else: blink_timer = 0
        blink_timer += 1

        NAME_GAME = title_font.render("INVARDERS ROBOT", 1, (255,255,255))
        screen.blit(NAME_GAME, (screen_width/2 - NAME_GAME.get_width()/2, 0))

        NAME_TEAM = title_font.render("TEAM 3 GÀ", 1, (255,255,255))
        screen.blit(NAME_TEAM, (screen_width/2 - NAME_TEAM.get_width()/2, 70))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                background_fx.stop()
                main()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    background_fx.stop()
                if event.key == pygame.K_F2:
                    background_fx.play()



    pygame.quit()


main_menu()