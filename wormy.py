# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 1200
WINDOWHEIGHT = 900
CELLSIZE = 30
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

NUM_APPLES = 5

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
BLUE      = (  0,   0, 255)
DARKBLUE  = (  0,   0, 155)
DARKGRAY  = ( 40,  40,  40)
YELLOW    = (255, 255,   0)
DARKYELLOW= (155, 155,   0)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Totally-Not-Wormy')

    showStartScreen()
    while True:
        score = runGame()
        showGameOverScreen(score)


def runGame():
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [[{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}],

                  [{'x': CELLWIDTH - startx, 'y': CELLHEIGHT - starty},
                   {'x': CELLWIDTH - startx - 1, 'y': CELLHEIGHT - starty},
                   {'x': CELLWIDTH - startx - 2, 'y': CELLHEIGHT - starty}]
                  ]
    direction = [RIGHT, RIGHT]
    score = [0, 0]
    powerupTracker = [0, 0]

    # Start the apples in a random place.
    apples = []
    for i in range(NUM_APPLES):
        apples.append(getRandomLocation())

    powerup = getRandomLocation()

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT) and direction[0] != RIGHT:
                    direction[0] = LEFT
                elif (event.key == K_RIGHT) and direction[0] != LEFT:
                    direction[0] = RIGHT
                elif (event.key == K_UP) and direction[0] != DOWN:
                    direction[0] = UP
                elif (event.key == K_DOWN) and direction[0] != UP:
                    direction[0] = DOWN
                elif (event.key == K_a) and direction[1] != RIGHT:
                    direction[1] = LEFT
                elif (event.key == K_d) and direction[1] != LEFT:
                    direction[1] = RIGHT
                elif (event.key == K_w) and direction[1] != DOWN:
                    direction[1] = UP
                elif (event.key == K_s) and direction[1] != UP:
                    direction[1] = DOWN
                elif (event.key == K_KP4):
                    if direction[0] != RIGHT:
                        direction[0] = LEFT
                    if direction[1] != RIGHT:
                        direction[1] = LEFT
                elif (event.key == K_KP6):
                    if direction[0] != LEFT:
                        direction[0] = RIGHT
                    if direction[1] != LEFT:
                        direction[1] = RIGHT
                elif (event.key == K_KP8):
                    if direction[0] != DOWN:
                        direction[0] = UP
                    if direction[1] != DOWN:
                        direction[1] = UP
                elif (event.key == K_KP2):
                    if direction[0] != UP:
                        direction[0] = DOWN
                    if direction[1] != UP:
                        direction[1] = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        if wormCoords[0][HEAD] == wormCoords[1][HEAD]:
            if sum(powerupTracker) > 0:
                if powerupTracker[0] > 0:
                    score[1] = score[1] - 2
                    score[0] = score[0] + 2
                else:
                    score[0] = score[0] - 2
                    score[1] = score[1] + 2
            else:
                score[0] = score[0] - 2
                score[1] = score[1] - 2
            return score # game over, both worms at fault for hitting eachother at same time
        if wormCoords[0][HEAD]['x'] == -1 or wormCoords[0][HEAD]['x'] == CELLWIDTH or wormCoords[0][HEAD][
            'y'] == -1 or wormCoords[0][HEAD]['y'] == CELLHEIGHT:
            score[0] = score[0] - 2
            return score # game over, worm 1's fault for hitting wall
        for wormBody in wormCoords[0][1:]:
            if wormBody['x'] == wormCoords[0][HEAD]['x'] and wormBody['y'] == wormCoords[0][HEAD]['y']:
                score[0] = score[0] - 2
                return score # game over, worm 1's fault for hitting itself
        if wormCoords[0][HEAD] in wormCoords[1]:
            if powerupTracker[0] > 0:
                score[1] = score[1] - 2
                score[0] = score[0] + 2
            else:
                score[0] = score[0] - 2
            return score  # game over, worm 1's fault for hitting worm 2
        if wormCoords[1][HEAD]['x'] == -1 or wormCoords[1][HEAD]['x'] == CELLWIDTH or wormCoords[1][HEAD]['y'] == -1 or \
                wormCoords[1][HEAD]['y'] == CELLHEIGHT:
            score[1] = score[1] - 2
            return score # game over, worm 2's fault for hitting wall or itself
        for wormBody in wormCoords[1][1:]:
            if wormBody['x'] == wormCoords[1][HEAD]['x'] and wormBody['y'] == wormCoords[1][HEAD]['y']:
                score[1] = score[1] - 2
                return score # game over, worm 2's fault for hitting itself
        if wormCoords[1][HEAD] in wormCoords[0]:
            if powerupTracker[1] > 0:
                score[0] = score[0] - 2
                score[1] = score[1] + 2
            else:
                score[1] = score[1] - 2
            return score  # game over, worm 2's fault for hitting worm 1

        # check if worm has eaten an apply
        apples[:] = [x for x in apples if not appleCollision(wormCoords[0], x)]
        if len(apples) < NUM_APPLES:
            apples.append(getRandomLocation())
            score[0] = score[0] + 1
        else:
            del wormCoords[0][-1] # remove worm's tail segment

        # check if worm 2 has eaten an apply
        apples[:] = [x for x in apples if not appleCollision(wormCoords[1], x)]
        if len(apples) < NUM_APPLES:
            apples.append(getRandomLocation())
            score[1] = score[1] + 1
        else:
            del wormCoords[1][-1]  # remove worm's tail segment

        # check if worm has eaten powerup
        if wormCoords[0][HEAD]['x'] == powerup['x'] and wormCoords[0][HEAD]['y'] == powerup['y']:
            powerupTracker[0] = FPS * 4
            powerup = getRandomLocation()

        # check if worm 2 has eaten powerup
        if wormCoords[1][HEAD]['x'] == powerup['x'] and wormCoords[1][HEAD]['y'] == powerup['y']:
            powerupTracker[1] = FPS * 4
            powerup = getRandomLocation()

        # move the worm by adding a segment in the direction it is moving
        if direction[0] == UP:
            newHeadA = {'x': wormCoords[0][HEAD]['x'], 'y': wormCoords[0][HEAD]['y'] - 1}
        elif direction[0] == DOWN:
            newHeadA = {'x': wormCoords[0][HEAD]['x'], 'y': wormCoords[0][HEAD]['y'] + 1}
        elif direction[0] == LEFT:
            newHeadA = {'x': wormCoords[0][HEAD]['x'] - 1, 'y': wormCoords[0][HEAD]['y']}
        elif direction[0] == RIGHT:
            newHeadA = {'x': wormCoords[0][HEAD]['x'] + 1, 'y': wormCoords[0][HEAD]['y']}
        wormCoords[0].insert(0, newHeadA)
        if direction[1] == UP:
            newHeadB = {'x': wormCoords[1][HEAD]['x'], 'y': wormCoords[1][HEAD]['y'] - 1}
        elif direction[1] == DOWN:
            newHeadB = {'x': wormCoords[1][HEAD]['x'], 'y': wormCoords[1][HEAD]['y'] + 1}
        elif direction[1] == LEFT:
            newHeadB = {'x': wormCoords[1][HEAD]['x'] - 1, 'y': wormCoords[1][HEAD]['y']}
        elif direction[1] == RIGHT:
            newHeadB = {'x': wormCoords[1][HEAD]['x'] + 1, 'y': wormCoords[1][HEAD]['y']}
        wormCoords[1].insert(0, newHeadB)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorms(wormCoords, powerupTracker)
        for apple in apples:
            drawApple(apple)
        if sum(powerupTracker) > 0:
            if powerupTracker[0] > 0:
                powerupTracker[0] = powerupTracker[0] - 1
            else:
                powerupTracker[1] = powerupTracker[1] - 1
        else:
            drawPowerup(powerup)
        drawScore(score)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def appleCollision(wormCoords, apple):
    if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
        return True
    else:
        return False

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Totally-Not-Wormy!', True, BLACK, GREEN)
    titleSurf2 = titleFont.render('Totally-Not-Wormy!', True, RED)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen(score):
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    scoreSurf = BASICFONT.render('Green Score: %s   Blue Score: %s' % (score[0], score[1]), True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    scoreRect = scoreSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 100)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 100 + 25)
    scoreRect.midtop = (WINDOWWIDTH / 2, 450)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    DISPLAYSURF.blit(scoreSurf, scoreRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score):
    scoreSurf = BASICFONT.render('Green Score: %s   Blue Score: %s' % (score[0], score[1]), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 280, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawWorms(wormCoords, powerupTracker):
    if powerupTracker[0] > 0:
        if powerupTracker[0] < FPS:
            if powerupTracker[0] % 2 == 0:
                drawWorm(wormCoords[0], [DARKGREEN, GREEN])
            else:
                drawWorm(wormCoords[0], [DARKYELLOW, YELLOW])
        else:
            drawWorm(wormCoords[0], [DARKYELLOW, YELLOW])
    else:
        drawWorm(wormCoords[0], [DARKGREEN, GREEN])
    if powerupTracker[1] > 0:
        if powerupTracker[1] < FPS:
            if powerupTracker[1] % 2 == 0:
                drawWorm(wormCoords[1], [DARKBLUE, BLUE])
            else:
                drawWorm(wormCoords[1], [DARKYELLOW, YELLOW])
        else:
            drawWorm(wormCoords[1], [DARKYELLOW, YELLOW])
    else:
        drawWorm(wormCoords[1], [DARKBLUE, BLUE])

def drawWorm(wormCoords, colors):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, colors[0], wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, colors[1], wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)

def drawPowerup(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    powerRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, YELLOW, powerRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()