import os

import pygame
from config import *

all_sprites = pygame.sprite.Group()
monsters = pygame.sprite.Group()
bullets = pygame.sprite.Group()
walls = pygame.sprite.Group()


def cut_sheet(sheet, columns, rows):
    width = sheet.get_width()
    height = sheet.get_height()
    w, h = width // columns, height // rows
    out = []
    for row in range(height // h):
        arr = []
        for column in range(width // w):
            fragment = sheet.subsurface((column * w, row * h, w, h))
            fragment = pygame.transform.scale(fragment, (32, 32))
            arr.append(fragment)
        out.append(arr)

    return out


def load_image(name, colorkey=None, scale=True):
    image = pygame.image.load(name)
    if scale:
        image = pygame.transform.scale(image, (PLATFORM_WIDTH, PLATFORM_HEIGHT))
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


idle_animation = [load_image(f"data/Little Mage/Idle/{i}", colorkey=-1) for i in os.listdir("data/Little Mage/Idle")]
run_animation = [load_image(f"data/Little Mage/Run/{i}", colorkey=-1) for i in os.listdir("data/Little Mage/Run")]
jumping_animation = [load_image(f"data/Little Mage/Rising - Jumping/{i}", colorkey=-1) for i in
                     os.listdir("data/Little Mage/Rising - Jumping")]


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, velocity, image="data/Retro Impact Effect Pack 5 A.png"):
        self.animation = cut_sheet(load_image(image, scale=False), 9, 30)[8]
        self.count = 0
        pygame.sprite.Sprite.__init__(self)
        bullets.add(self)
        all_sprites.add(self)
        self.rect = pygame.Rect(pos[0], pos[1], PLATFORM_WIDTH / 2, PLATFORM_HEIGHT / 2)
        self.velocity = velocity

    def update(self):
        self.rect.x += self.velocity
        self.count = (self.count + 1) % 4
        if self.velocity > 0:
            self.image = self.animation[self.count]
        else:
            self.image = pygame.transform.flip(self.animation[self.count], 1, 0)
            self.image.set_colorkey(self.image.get_at((0, 0)))
        if pygame.sprite.spritecollide(self, walls, dokill=False):
            self.kill()


class Player(pygame.sprite.Sprite):

    def __init__(self, x=32, y=32):
        self.animation = idle_animation
        self.count = 0
        self.image = self.animation[self.count]
        self.maxYVal = 60
        self.GRAVITY = 2
        self.JUMP_POWER = 5
        self.max_jump = 15
        self.is_jumping = False
        self.xvel = 0
        self.yvel = 0
        self.speed = 10
        self.direction = 1
        pygame.sprite.Sprite.__init__(self)
        self.color = (255, 200, 0)
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        self.onGround = False

    def move(self, left, right, up):
        if not (left and right and up):
            self.animation = idle_animation
        if (left or right) and not up:
            self.animation = run_animation
        self.count += 0.25
        if self.count >= len(self.animation):
            self.count = 0
        if up:
            if self.onGround:
                self.is_jumping = True
            else:
                self.animation = jumping_animation
        else:
            self.is_jumping = False
        if self.is_jumping:
            self.yvel -= self.JUMP_POWER
        if self.yvel <= -self.max_jump:
            self.is_jumping = False
        if left:
            self.xvel = -self.speed
            self.direction = -1
        if right:
            self.xvel = self.speed
            self.direction = 1
        if not (left or right):
            self.xvel = 0
        if not self.onGround:
            self.yvel += self.GRAVITY
        self.onGround = False
        if self.yvel > self.maxYVal:
            self.yvel = self.maxYVal
        self.rect.y += self.yvel
        self.collide(0, self.yvel)
        self.rect.x += self.xvel
        self.collide(self.xvel, 0)
        self.image = self.animation[int(self.count)]
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, 1, 0)
            self.image.set_colorkey(self.image.get_at((0, 0)))

    def collide(self, xvel, yvel):
        for wall in walls:
            if pygame.sprite.collide_rect(wall, self):
                if xvel > 0:
                    self.rect.right = wall.rect.left
                if xvel < 0:
                    self.rect.left = wall.rect.right
                if yvel > 0:
                    self.rect.bottom = wall.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = wall.rect.bottom
                    self.yvel = 0
                    self.is_jumping = False

    def attach(self):
        if bullets.__len__() < 3:
            if self.direction:
                Bullet((self.rect.left, self.rect.top), self.direction * 10)
            else:
                Bullet((self.rect.right, self.rect.top), self.direction * 10)


class Wall(pygame.sprite.Sprite):

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        walls.add(self)
        self.color = (255, 255, 255)
        self.rect = pygame.Rect(pos[0], pos[1], PLATFORM_WIDTH, PLATFORM_HEIGHT)


class EndPoint(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.color = (255, 0, 0)
        self.rect = pygame.Rect(pos[0], pos[1], 16, 16)
