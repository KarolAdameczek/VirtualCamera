import pygame
from tasks import DrawLineTask
from models import Camera

pygame.init()

LINE_WIDTH = 2

TRANSLATION_SPEED = 1
ROTATION_SPEED = 0.001
ZOOMSPEED = 0.001

class Engine():
    keys_pressed = set()

    def __init__(self, sizex, sizey):
        self.camera = Camera()
        self.screen = pygame.display.set_mode([sizex, sizey])
        self.translation = (sizex/2, sizey/2)

    def handleTask(self, task):
        return {
            DrawLineTask : self.drawLine
        }[type(task)](task)
        

    def drawLine(self, task):
        start = ( 
            task.start[0] + self.translation[0],
            task.start[1] + self.translation[1]
        )

        end = ( 
            task.end[0] + self.translation[0],
            task.end[1] + self.translation[1]
        )

        pygame.draw.line(
            self.screen, 
            task.color, 
            start,
            end,
            LINE_WIDTH)

    def handleTranslations(self, event):
        if pygame.K_LEFT in self.keys_pressed:
            self.camera.translateX(-TRANSLATION_SPEED)
        if pygame.K_RIGHT in self.keys_pressed:
            self.camera.translateX(TRANSLATION_SPEED)
        if pygame.K_PAGEUP in self.keys_pressed:
            self.camera.translateY(-TRANSLATION_SPEED)
        if pygame.K_PAGEDOWN in self.keys_pressed:
            self.camera.translateY(TRANSLATION_SPEED)
        if pygame.K_UP in self.keys_pressed:
            self.camera.translateZ(TRANSLATION_SPEED)
        if pygame.K_DOWN in self.keys_pressed:
            self.camera.translateZ(-TRANSLATION_SPEED)

    def handleRotations(self, event):
        if pygame.K_w in self.keys_pressed:
            self.camera.rotateX(-ROTATION_SPEED)
        if pygame.K_s in self.keys_pressed:
            self.camera.rotateX(ROTATION_SPEED)
        if pygame.K_d in self.keys_pressed:
            self.camera.rotateY(-ROTATION_SPEED)
        if pygame.K_a in self.keys_pressed:
            self.camera.rotateY(ROTATION_SPEED)
        if pygame.K_q in self.keys_pressed:
            self.camera.rotateZ(-ROTATION_SPEED)
        if pygame.K_e in self.keys_pressed:
            self.camera.rotateZ(ROTATION_SPEED)

    def handleZooming(self, event):
        if pygame.K_z in self.keys_pressed:
            self.camera.changeZoom(self.camera.zoom * ZOOMSPEED)
        if pygame.K_x in self.keys_pressed:
            self.camera.changeZoom(-self.camera.zoom * ZOOMSPEED)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.keys_pressed.add(event.key)
                elif event.type == pygame.KEYUP:
                    self.keys_pressed.remove(event.key)

            self.handleTranslations(event)
            self.handleRotations(event)
            self.handleZooming(event)
            self.screen.fill((0,0,0))

            tasks = self.camera.getTasks()

            for task in tasks:
                self.handleTask(task)

            #pygame.draw.line(self.screen, (255,255,255), (0,0), (250, 250), 2)
            #pygame.draw.circle(self.screen, (0, 0, 255), (250, 250), 75)

            pygame.display.flip()
        pygame.quit()