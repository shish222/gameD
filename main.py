import sys

import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, image, size):
        pygame.sprite.Sprite.__init__(self)
        super().__init__()
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.pos = [0, 0]
        self.speed = 1

    def update(self):
        # self.pos[0] += self.speed
        # self.pos[1] += self.speed
        # self.rect.move_ip(self.pos)
        # if self.rect.left < 0:
        #     self.speed = -self.speed
        # if self.rect.right > 500:
        #     self.speed = self.speed
        # if self.rect.top < 0:
        #     self.speed = -self.speed
        # if self.rect.bottom > 500:
        #     self.speed = self.speed
        # # self.rect.move_ip(self.pos)
        screen.blit(self.image, self.pos)

    def move(self, pos):
        self.pos = pos


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, but=1, image=None,
                 colorText: [int, int, int, int] = [255, 255, 255, 10], image_hover=None):
        pygame.sprite.Sprite.__init__(self)
        if image:
            self.image = pygame.image.load(image)
            self.image = pygame.transform.scale(self.image, [width, height])
        if image_hover:
            self.image_hover = pygame.image.load(image_hover)
            self.image_hover = pygame.transform.scale(self.image_hover, [width, height])
        self.but = but
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
            # self.image.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
            if self.image_hover:
                screen.blit(self.image_hover, self.buttonRect)
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if not self.alreadyPressed:
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


class Game:
    def __init__(self):
        global screen
        pygame.init()
        pygame.display.set_caption("Simple Game")
        screen = pygame.display.set_mode((500, 500))
        self.clock = pygame.time.Clock()
        self.playerGroup = pygame.sprite.Group()
        # self.playerGroup.add(Player(image="goldappl.png", size=[100, 100]))
        self.buttonGroup = pygame.sprite.Group()
        self.buttonGroup.add(Button(100, 100, 50, 50, image="goldappl.png", onclickFunction=lambda: print("sdfd"),image_hover = "i.webp"))
        self.running = True
        self.clock.tick(60)

    def run(self):
        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                    pygame.display.quit()
            self.update()

    def update(self):
        # self.playerGroup.sprites()[0].move((100, 100))
        screen.fill((0, 0, 0))
        self.playerGroup.update()
        self.buttonGroup.update()
        # self.playerGroup.draw(screen)
        pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
