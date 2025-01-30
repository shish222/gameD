import levels
from sprites import *


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
            self.revers_image = pygame.transform.flip(self.image, True, False)
            self.revers_image.set_colorkey(self.image.get_at((0, 0)))
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
                screen.blit(self.revers_image, camera.apply(self))
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
clock = pygame.time.Clock()
left = right = False  # по умолчанию - стоим
up = False
levelId = 0
level = levels.levels[levelId]
end_rect, player, camera = generate_level(level)
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
        if e.type == pygame.KEYDOWN and e.key == pygame.K_a:
            player.attach()
        if e.type == pygame.KEYUP and e.key == pygame.K_UP:
            up = False
        if e.type == pygame.KEYUP and e.key == pygame.K_RIGHT:
            right = False
        if e.type == pygame.KEYUP and e.key == pygame.K_LEFT:
            left = False
    if player.rect.colliderect(end_rect.rect):
        all_sprites.empty()
        monsters.empty()
        bullets.empty()
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
    bullets.update()
    for i in all_sprites:
        try:
            # pygame.draw.rect(screen, i.image, camera.apply(i))
            screen.blit(i.image, camera.apply(i))
        except Exception:
            pygame.draw.rect(screen, i.color, camera.apply(i))
    monsters.update(screen)
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
