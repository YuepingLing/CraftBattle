import pygame
from pygame.locals import *
import random
import os

# constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 153, 0)
BLUE = (0, 102, 255)

RES = os.path.join(os.path.dirname(os.path.realpath(__file__)), "res")
# __name__ == "__main__"

# pygame display set up
pygame.init()

WIDTH, HEIGHT = 580, 720  # soft code
display = pygame.display.set_mode((WIDTH, HEIGHT))
# display = pygame.display.set_mode((960, 800))

clock = pygame.time.Clock()
FPS = 40  # frames per sec

FONT = pygame.font.Font(None, 32)
BUTTON_FONT = pygame.font.Font(None, 45)

craft_img = pygame.image.load(os.path.join(RES, "craft.png"))  # load -> pygame.Surface instance
enemy_img = pygame.image.load(os.path.join(RES, "enemy.png"))


class GameObj(pygame.sprite.Sprite):
    family = pygame.sprite.RenderUpdates()

    def __init__(self):
        super().__init__()
        GameObj.family.add(self)


class Button(GameObj):

    all = pygame.sprite.Group()

    def __init__(self, text, centerx, centery):
        super().__init__()
        self.text = text
        bit_map = BUTTON_FONT.render(text, True, BLACK)
        text_rect = bit_map.get_rect()
        surf_size = [val + 10 for val in bit_map.get_size()]
        self.image = pygame.Surface(surf_size)
        self.rect = self.image.get_rect()
        self.image.fill(WHITE)
        pygame.draw.rect(self.image, BLACK, self.rect, 3)
        text_rect.center = [int(val / 2) for val in self.image.get_size()]
        self.image.blit(bit_map, text_rect)
        self.rect.center = (centerx, centery)


class Player(GameObj):
    WIDTH = 50
    HEIGHT = 50
    SPEED = 8
    FIRE_RATE = 8

    score = 0

    r = None

    def __init__(self):
        super().__init__()
        self.image = craft_img
        self.rect = self.image.get_rect()  # where to draw
        self.rect.bottom = HEIGHT
        self.rect.centerx = WIDTH / 2
        self.x, self.y = self.rect.center
        self._fire_timer = 0
        Player.r = self

    def update(self):

        # control
        if key_state[K_a]:
            self.x -= Player.SPEED
        if key_state[K_d]:
            self.x += Player.SPEED
        if key_state[K_SPACE]:
            if self._fire_timer <= 0:
                self.fire()

        # renew position and restriction
        self.rect.centerx = self.x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        elif self.rect.left < 0:
            self.rect.left = 0
        self.x = self.rect.centerx
        self._fire_timer -= 1

        # enemy crash
        if pygame.sprite.spritecollide(self, Enemy.family, False):
            self.kill()

    def fire(self):
        self._fire_timer = Player.FIRE_RATE
        Bullet(*self.rect.midtop)


class Enemy(GameObj):
    WIDTH = 30
    HEIGHT = 40
    SPEED = 5

    family = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()  # pygame.Rect(0, 0, w, h)
        self.rect.bottom = 0
        self.rect.left = random.randint(0, WIDTH - Enemy.WIDTH)
        Enemy.family.add(self)

    def update(self):
        self.rect.move_ip(0, Enemy.SPEED)
        if pygame.sprite.spritecollide(self, Bullet.family, True):
            self.kill()
            Player.score += 1
            Enemy()
        if self.rect.top > HEIGHT:
            self.kill()
            Enemy()


class Bullet(GameObj):
    WIDTH = 4
    LENGTH = 20
    SPEED = 20

    family = pygame.sprite.Group()

    def __init__(self, x, y, facing=-1):
        super().__init__()
        self.image = pygame.Surface((Bullet.WIDTH, Bullet.LENGTH))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.rect.center = x, y
        self.speed = facing * Bullet.SPEED
        Bullet.family.add(self)

    def update(self):
        self.y += self.speed
        self.rect.centery = self.y
        if self.rect.top > HEIGHT or self.rect.bottom < 0:
            self.kill()


def label(surface, text, x, y, text_color=BLACK):
    bit_map = FONT.render(text, True, text_color)
    rect = bit_map.get_rect()
    rect.topleft = (x, y)
    if x < 0 or y < 0:
        rect.center = (WIDTH / 2, HEIGHT / 2)
    surface.blit(bit_map, rect)


def retry():
    # clear sprites
    for enemy in Enemy.family.sprites():
        enemy.kill()
    for bullet in Bullet.family.sprites():
        bullet.kill()
    Player.score = 0

    label(display, "Tap R to retry!", -1, -1)
    pygame.display.flip()

    loop = True
    while loop:
        # control
        for event in pygame.event.get():
            if event.type == QUIT:
                quit_all()
            elif event.type == KEYDOWN:
                if event.key == K_q and event.mod & KMOD_META:
                    quit_all()
                if event.key == K_r:
                    Player()
                    Enemy()
                    Enemy()
                    Enemy()
                    Enemy()
                    return


def main():
    global key_state

    Player()
    Enemy()
    Enemy()
    Enemy()
    Enemy()

    Button("HELLO WORLD", 300, 300)

    loop = True
    while loop:
        # clear
        display.fill(WHITE)

        # control
        for event in pygame.event.get():
            if event.type == QUIT:
                quit_all()
            elif event.type == KEYDOWN:
                if event.key == K_q and event.mod & KMOD_META:
                    quit_all()

        key_state = pygame.key.get_pressed()

        # update
        GameObj.family.update()
        label(display, "score: " + str(Player.score), 0, 0)
        if not Player.r.alive():
            retry()

        # render
        GameObj.family.draw(display)
        pygame.display.flip()

        clock.tick(FPS)


def quit_all():
    pygame.quit()
    quit()


main()
