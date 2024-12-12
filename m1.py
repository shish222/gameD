class Button1():
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, but=1):
        self.but = but
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.fillColors = {'normal': (18, 229, 64), 'hover': (44, 184, 74), 'pressed': '#333333', }
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.main_front = pygame.font.Font(None, 32)
        self.buttonSurf = self.main_front.render(buttonText, True, (20, 20, 20))
        self.alreadyPressed = False
        objects.append(self)

    def process(self):
        mousePos = pg.mouse.get_pos()
        butm = pg.key.get_pressed()
        if butm[self.but]:
            self.onclickFunction()
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if pg.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False
        self.buttonSurface.blit(self.buttonSurf, [self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
                                                  self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2])
        sr.blit(self.buttonSurface, self.buttonRect)
