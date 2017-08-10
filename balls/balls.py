import sys
import math
import random
from itertools import combinations

import pygame
from pygame.locals import *

pygame.init()
WINDOWSIZE = WINWIDTH, WINHEIGHT = (800, 600)
FPS = 30 
fps_clock = pygame.time.Clock()
display = pygame.display.set_mode(WINDOWSIZE)
pygame.display.set_caption('Ball Simulator')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT = pygame.font.Font('freesansbold.ttf', 16)
RADIUS = 50
BALL_IMG = pygame.image.load("images/ball.png")
BALL_IMG = pygame.transform.scale(BALL_IMG, (2*RADIUS, 2*RADIUS))
MAXVEL = 4

def distance_from(p, op):
    x, y = p
    ox, oy = op
    return ((x-ox)**2 + (y-oy)**2)**0.5

def direction_towards(p, op):
    x, y = p
    ox, oy = op
    if x-ox == 0:
        if y > oy:
            return 3*math.pi/2
        else:
            return math.pi/2
    angle = math.atan((y-oy) / (x-ox))
    if x > ox:
        angle = math.pi + angle
    angle = angle % (math.pi*2)
    return angle

class Ball:
    def __init__(self, x=None, y=None, vx=None, vy=None, mass=1):
        self.image = BALL_IMG
        self.rect = self.image.get_rect()
        if x is None:
            x = random.randint(RADIUS, WINWIDTH-RADIUS)
        if y is None:
            y = random.randint(RADIUS, WINHEIGHT-RADIUS)
        if vx is None and vy is None:
            vx, vy = randomVelocity()
        self.pos = (x, y)
        self.vel = (vx, vy)
        self.mass = mass

    @property
    def pos(self):
        return self.rect.center

    @pos.setter
    def pos(self, pos):
        self.rect.center = pos

    @property
    def vel(self):
        return self.vx, self.vy

    @vel.setter
    def vel(self, vel):
        self.vx, self.vy = vel

    # def collide(self, angle):
    #     vx, vy = self.vel
    #     v = distance_from((0, 0), (vx, vy))
    #     a = direction_towards((vx, vy), (0, 0))
    #     a = (2*angle - a) % (math.pi*2)
    #     angle = (angle+math.pi) % (math.pi*2)
    #     self.vel = (v*math.cos(a), v*math.sin(a))

    def tick(self, bouncywalls):
        WALL_BOUNCY = 0.01
        x, y = self.pos
        vx, vy = self.vel
        x += vx
        y += vy
        if bouncywalls:
            if x < RADIUS:
                vx += WALL_BOUNCY * (x-RADIUS)**2
            if x > WINWIDTH-RADIUS:
                vx -= WALL_BOUNCY * (x-WINWIDTH+RADIUS)**2
            if y < RADIUS:
                vy += WALL_BOUNCY * (y-RADIUS)**2
            if y > WINHEIGHT-RADIUS:
                vy -= WALL_BOUNCY * (y-WINHEIGHT+RADIUS)**2
        self.pos = (x, y)
        self.vel = (vx, vy)

    def should_die(self):
        x, y = self.pos
        return x < -RADIUS or x > WINWIDTH+RADIUS or \
            y < -RADIUS or y > WINHEIGHT+RADIUS
        
    def render(self):
        display.blit(self.image, self.rect)

    # def interact_naw(self, otherball):
    #     if distance_from(self.pos, otherball.pos) <= 2*RADIUS:
    #         self.collide(direction_towards(self.pos, otherball.pos))
    #         otherball.collide(direction_towards(otherball.pos, self.pos))

    def interact(self, otherball):
        d = 2*RADIUS - distance_from(self.pos, otherball.pos)
        if d > 0:
            f = 0.01 * d**2
            angle = direction_towards(self.pos, otherball.pos)
            self.vx -= f*math.cos(angle) / self.mass
            self.vy -= f*math.sin(angle) / self.mass
            otherball.vx += f*math.cos(angle) / otherball.mass
            otherball.vy += f*math.sin(angle) / otherball.mass

    def debug(self):
        print("x: {0[0]} y: {0[1]} vx: {1[0]} vy: {1[1]}".format(self.pos, self.vel))

def randomVelocity():
    vx = random.randint(-MAXVEL, MAXVEL)
    vy = ((random.randint(0,1)*2) - 1) * (MAXVEL**2-vx**2)**0.5
    return (vx, vy)

def spawnball(balls):
    for i in range(10):
        collides = False
        newball = Ball() #empty constructor does randomization
        if not any(distance_from(b.pos, newball.pos) <= 2*RADIUS for b in balls):
            balls.append(newball)
            break

def scene1():
    return [
        Ball(x=200, y=200, vx=5, vy=0, mass=2),
        Ball(x=500, y=200, vx=0, vy=0, mass=1)]

def scene2():
    return [
        Ball(x=200, y=200, vx=5, vy=0, mass=1),
        Ball(x=500, y=150, vx=-5, vy=0, mass=1),
        Ball(x=500, y=250, vx=-5, vy=0, mass=1)]

def scene3():
    return [
        Ball(x=200, y=200, vx=5, vy=0, mass=1),
        Ball(x=450, y=200, vx=0, vy=0, mass=1),
        Ball(x=550, y=200, vx=0, vy=0, mass=1)]

def main():
    balls = []
    bouncywalls = False
    paused = False
    tick_once = False
    while True:
        display.fill(WHITE)
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    spawnball(balls)
                elif event.key == K_q:
                    bouncywalls = not bouncywalls
                elif event.key == K_1:
                    balls = scene1()
                elif event.key == K_2:
                    balls = scene2()
                elif event.key == K_3:
                    balls = scene3()
                elif event.key == K_c:
                    balls = []
                    scene = 0
                elif event.key == K_p:
                    paused = not paused
                elif event.key == K_n:
                    tick_once = True
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
            elif event.type == QUIT:
                pygame.quit()
                sys.exit(0)
        n = len(balls)
        p = [0., 0.]
        if not paused or tick_once:
            tick_once = False
            for b in tuple(balls):
                b.tick(bouncywalls)
                if b.should_die():
                    balls.remove(b)
            for b, ob in combinations(balls, 2):
                b.interact(ob)

        for b in balls:
            p[0] += b.vx*b.mass
            p[1] += b.vy*b.mass
            b.render()

        textsurf = FONT.render(get_text(p, bouncywalls, paused), True, BLACK) 
        textrect = textsurf.get_rect()
        textrect.center = (math.ceil(WINWIDTH/2), WINHEIGHT-50)
        display.blit(textsurf, textrect)
        pygame.display.update()
        fps_clock.tick(FPS)  
        pygame.display.flip()

def get_text(momentum, bouncywalls, paused):
    return "Px={0[0]:0.03} Py={0[1]:0.03} WALLS {1}ABLED {2}".format(
        momentum, "EN" if bouncywalls else "DIS", "PAUSED" if paused else "")

if __name__ == '__main__':
    main()