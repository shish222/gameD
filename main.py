import sys

import levels
from sprites import *


def terminate():
    pygame.quit()
    sys.exit()


class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=2, _len=0, image="Slime Sprites.png", colorkey=None):
        pygame.sprite.Sprite.__init__(self)
        self.animation = cut_sheet(load_image(image, scale=False, colorkey=-1), 4, 3)[0][:2]
        self.speed = speed
        self._len = _len
        self.color = (0, 0, 255)
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        self.count = 0
        self.count2 = 0
        self.image = self.animation[self.count2]

    def update(self, screen):
        self.count2 += 0.25
        if self.count2 >= len(self.animation):
            self.count2 = 0
        self.image = self.animation[int(self.count2)]
        self.image = self.image.subsurface(self.image.get_bounding_rect())
        self.image = pygame.transform.scale(self.image, (PLATFORM_WIDTH, PLATFORM_HEIGHT))
        if self.count >= self._len and self._len > 0:
            self.count = 0
            self.speed = -self.speed
        elif self._len > 0:
            self.rect.x += self.speed
            self.count += abs(self.speed)

        if self.speed > 0:
            screen.blit(self.image, camera.apply(self))
        else:
            revers_image = pygame.transform.flip(self.image, True, False)
            revers_image.set_colorkey(revers_image.get_at((0, 0)))
            screen.blit(revers_image, camera.apply(self))


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
                    monsters.add(monster)
            if col == "P":
                player = Player(x, y)
                all_sprites.add(player)
            x += PLATFORM_WIDTH
        y += PLATFORM_HEIGHT
        x = 0
    m_l_w = max([len(i) for i in level["map"]])
    total_level_width = m_l_w * PLATFORM_WIDTH
    total_level_height = len(level["map"]) * PLATFORM_HEIGHT
    camera = Camera(camera_configure, total_level_width, total_level_height)
    return end_rect, player, camera


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, image=None,
                 colorText: [int, int, int, int] = [255, 255, 255, 10], image_hover=None):
        pygame.sprite.Sprite.__init__(self)
        if image:
            self.image = pygame.image.load(image)
            self.image = pygame.transform.scale(self.image, [width, height])
        else:
            self.image = None
        if image_hover:
            self.image_hover = pygame.image.load(image_hover)
            self.image_hover = pygame.transform.scale(self.image_hover, [width, height])
        else:
            self.image_hover = None
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colorText = colorText
        self.buttonText = buttonText
        self.onclickFunction = onclickFunction
        self.fillColors = {'normal': (18, 229, 64), 'hover': (44, 184, 74), 'pressed': '#333333', }
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.buttonRect.center = (self.x, self.y)
        self.main_front = pygame.font.Font(None, 32)
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonSurf = self.main_front.render(self.buttonText, True, self.colorText)
        self.alreadyPressed = False

    def update(self):
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.image:
            screen.blit(self.image, self.buttonRect)
        if self.buttonRect.collidepoint(pygame.mouse.get_pos()):
            self.buttonSurface.fill(self.fillColors['hover'])
            self.buttonSurf = self.main_front.render(self.buttonText, True, self.colorText)
            if self.image_hover:
                screen.blit(self.image_hover, self.buttonRect)
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if not self.alreadyPressed:
                    if self.onclickFunction:
                        self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False
        if self.image:
            self.textRect = self.buttonSurf.get_rect(center=self.buttonRect.center)
            screen.blit(self.buttonSurf, self.textRect)
        else:
            self.buttonSurface.blit(self.buttonSurf, [self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
                                                      self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2])
            screen.blit(self.buttonSurface, self.buttonRect)


def start_menu():
    btn_start = Button(WIN_WIDTH // 2, (WIN_HEIGHT // 2) - 60, 200, 50, image="button.png",
                       image_hover="buttonpress.png", buttonText="Начать игру", colorText=(0, 0, 0, 10))
    btn_exit = Button(WIN_WIDTH // 2, WIN_HEIGHT // 2, 200, 50, image="button.png",
                      image_hover="buttonpress.png", onclickFunction=terminate, buttonText="Выйти",
                      colorText=(0, 0, 0, 10))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        if btn_start.buttonRect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            return
        screen.fill((0, 0, 0))
        btn_start.update()
        btn_exit.update()
        pygame.display.update()


def dead_menu():
    btn_start = Button(WIN_WIDTH // 2, (WIN_HEIGHT // 2) - 60, 200, 50, image="button.png",
                       image_hover="buttonpress.png", buttonText="Начать заново", colorText=(0, 0, 0, 10))
    btn_exit = Button(WIN_WIDTH // 2, WIN_HEIGHT // 2, 200, 50, image="button.png",
                      image_hover="buttonpress.png", onclickFunction=terminate, buttonText="Выйти",
                      colorText=(0, 0, 0, 10))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        if btn_start.buttonRect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            all_sprites.empty()
            monsters.empty()
            bullets.empty()
            level = levels.levels[levelId]
            end_rect, player, camera = generate_level(level)
            return end_rect, player, camera
        screen.fill((0, 0, 0))
        btn_start.update()
        btn_exit.update()
        pygame.display.update()


pygame.init()
pygame.display.set_caption("GAME")
screen = pygame.display.set_mode(DISPLAY)
clock = pygame.time.Clock()
left = right = False
up = False
levelId = 0
level = levels.levels[levelId]
end_rect, player, camera = generate_level(level)
start_menu()
while True:
    clock.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            terminate()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            terminate()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_UP:
            up = True
        if e.type == pygame.KEYDOWN and e.key == pygame.K_LEFT:
            left = True
        if e.type == pygame.KEYDOWN and e.key == pygame.K_RIGHT:
            right = True
        if e.type == pygame.KEYDOWN and e.key == pygame.K_a:
            player.attach()
        if e.type == pygame.KEYUP and e.key == pygame.K_UP:
            up = False
        if e.type == pygame.KEYUP and e.key == pygame.K_RIGHT:
            right = False
        if e.type == pygame.KEYUP and e.key == pygame.K_LEFT:
            left = False
    pygame.sprite.groupcollide(monsters, bullets, True, True)
    if player.rect.colliderect(end_rect.rect):
        all_sprites.empty()
        monsters.empty()
        bullets.empty()
        walls.empty()
        levelId = level["next_level_id"]
        level = levels.levels[levelId]
        end_rect, player, camera = generate_level(level)

    screen.fill((0, 0, 0))
    if pygame.sprite.spritecollideany(player, monsters):
        left = right = up = False
        end_rect, player, camera = dead_menu()
    camera.update(player)
    player.move(left, right, up)
    bullets.update()
    for i in all_sprites:
        try:
            screen.blit(i.image, camera.apply(i))
        except Exception:
            pygame.draw.rect(screen, i.color, camera.apply(i))
    monsters.update(screen)
    pygame.display.flip()
    clock.tick(fps)
