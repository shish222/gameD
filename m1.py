import os
import sys
import pygame
import levels

WIN_WIDTH = 600  # Ширина создаваемого окна
WIN_HEIGHT = 600  # Высота
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
PLATFORM_WIDTH = PLATFORM_HEIGHT = 32
fps = 60


def load_image(name, colorkey=None):
    image = pygame.image.load(name)
    image = pygame.transform.scale(image, (PLATFORM_WIDTH, PLATFORM_HEIGHT))
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class Player(pygame.sprite.Sprite):

    def __init__(self, x=32, y=32):
        self.maxYVal = 60
        self.GRAVITY = 2
        self.JUMP_POWER = 6
        self.max_jump = 30
        self.is_jumping = False
        self.xvel = 0
        self.yvel = 0
        self.speed = 10
        pygame.sprite.Sprite.__init__(self)
        self.color = (255, 200, 0)
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        self.onGround = False

    def move(self, left, right, up):
        print(up, self.yvel, self.onGround)
        if up:
            if self.onGround:
                # self.yvel = -self.max_jump
                self.is_jumping = True
        else:
            self.is_jumping = False
        if self.is_jumping:
            self.yvel -= self.JUMP_POWER
        if self.yvel <= -self.max_jump:
            self.is_jumping = False
        if left:
            self.xvel = -self.speed
        if right:
            self.xvel = self.speed
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

    def kill(self):
        pass


class Wall(pygame.sprite.Sprite):

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        walls.append(self)
        self.color = (255, 255, 255)
        self.rect = pygame.Rect(pos[0], pos[1], PLATFORM_WIDTH, PLATFORM_HEIGHT)


class EndPoint(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.color = (255, 0, 0)
        self.rect = pygame.Rect(pos[0], pos[1], 16, 16)


class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=2, _len=0, image=None, colorkey=None):
        pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.image.load("data/")
        self.speed = speed
        self._len = _len
        self.color = (0, 0, 255)
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        if image != None:
            self.image = load_image(image, colorkey)
        self.count = 0

    def update(self, screen):
        if self.count >= self._len and self._len > 0:
            self.count = 0
            self.speed = -self.speed
        elif self._len > 0:
            self.rect.x += self.speed
            self.count += abs(self.speed)

        if self.image != None:
            if self.speed > 0:
                screen.blit(self.image, camera.apply(self))
            else:
                screen.blit(pygame.transform.flip(self.image, 1, 0), camera.apply(self))
        else:
            pygame.draw.rect(screen, self.color, camera.apply(self))


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIN_WIDTH / 2, -t + WIN_HEIGHT / 2

    l = min(0, l)  # Не движемся дальше левой границы
    l = max(-(camera.width - WIN_WIDTH), l)  # Не движемся дальше правой границы
    t = max(-(camera.height - WIN_HEIGHT), t)  # Не движемся дальше нижней границы
    t = min(0, t)  # Не движемся дальше верхней границы

    return pygame.Rect(l, t, w, h)


def generate_level(level):
    x = y = 0
    for row in level["map"]:
        for col in row:
            if col == "W":
                all_sprites.add(Wall((x, y)))
            if col == "E":
                end_rect = EndPoint((x, y))
                all_sprites.add(end_rect)
            if col.isdigit():
                if col in level["monsters"].keys():
                    m = level["monsters"][col]
                    monster = Monster(x, y, image=m["image"], _len=m["len"] * PLATFORM_WIDTH, colorkey=-1)
                    # all_sprites.add(monster)
                    monsters.add(monster)
            if col == "P":
                player = Player(x, y)
                all_sprites.add(player)
            x += PLATFORM_WIDTH
        y += PLATFORM_HEIGHT
        x = 0
    m_l_w = max([len(i) for i in level["map"]])
    total_level_width = m_l_w * PLATFORM_WIDTH  # Высчитываем фактическую ширину уровня
    total_level_height = len(level) * PLATFORM_HEIGHT  # высоту
    camera = Camera(camera_configure, total_level_width, total_level_height)
    return end_rect, player, camera


# Initialise pygame
os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()

# Set up the display
pygame.display.set_caption("Get to the red square!")
screen = pygame.display.set_mode(DISPLAY)
all_sprites = pygame.sprite.Group()
monsters = pygame.sprite.Group()
clock = pygame.time.Clock()
walls = []  # List to hold the walls
# player = Player()  # Create the player
# all_sprites.add(player)
left = right = False  # по умолчанию - стоим
up = False
levelId = 0
level = levels.levels[levelId]
end_rect, player, camera = generate_level(level)
# level = levels.levels[levelId]
# for row in level["map"]:
#     for col in row:
#         if col == "W":
#             all_sprites.add(Wall((x, y)))
#         if col == "E":
#             end_rect = EndPoint((x, y))
#             all_sprites.add(end_rect)
#         if col.isdigit():
#             if col in level["monsters"].keys():
#                 m = level["monsters"][col]
#                 monster = Monster(x, y, image=m["image"], _len=m["len"] * PLATFORM_WIDTH, colorkey=-1)
#                 # all_sprites.add(monster)
#                 monsters.add(monster)
#         x += PLATFORM_WIDTH
#     y += PLATFORM_HEIGHT
#     x = 0
# m_l_w = max([len(i) for i in level["map"]])
# total_level_width = m_l_w * PLATFORM_WIDTH  # Высчитываем фактическую ширину уровня
# total_level_height = len(level) * PLATFORM_HEIGHT  # высоту
# left = right = False  # по умолчанию - стоим
# up = False
# camera = Camera(camera_configure, total_level_width, total_level_height)
running = True
while running:
    clock.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            running = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_UP:
            up = True
        if e.type == pygame.KEYDOWN and e.key == pygame.K_LEFT:
            left = True
        if e.type == pygame.KEYDOWN and e.key == pygame.K_RIGHT:
            right = True

        if e.type == pygame.KEYUP and e.key == pygame.K_UP:
            up = False
        if e.type == pygame.KEYUP and e.key == pygame.K_RIGHT:
            right = False
        if e.type == pygame.KEYUP and e.key == pygame.K_LEFT:
            left = False
    if player.rect.colliderect(end_rect.rect):
        all_sprites.empty()
        monsters.empty()
        levelId = level["next_level_id"]
        level = levels.levels[levelId]
        end_rect, player, camera = generate_level(level)
        # pygame.quit()
        # sys.exit()
    screen.fill((0, 0, 0))
    if pygame.sprite.spritecollideany(player, monsters):
        player.kill()
    camera.update(player)
    player.move(left, right, up)
    for i in all_sprites:
        pygame.draw.rect(screen, i.color, camera.apply(i))
    monsters.update(screen)
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
