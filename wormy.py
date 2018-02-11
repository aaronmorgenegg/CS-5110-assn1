# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys, itertools

from math import sqrt
from pygame.locals import *


FPS = 60
WINDOWWIDTH = 1200
WINDOWHEIGHT = 900
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

NUM_APPLES = 20
APPLE_OPTION = 3
SHORT_TIME = 300
MIN_APPLE_DISTANCE = 15

APPLES = []
APPLE_TIMES = []
SCORE = 0
APPLE_OPTION_TIMER = 360 # needs to be a multiple of 12
APPLE_QUADRANT = random.randint(1, 5)

MAX_WORM_LENGTH = 10

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
        showGameOverScreen()


def runGame():
    global CELLWIDTH, CELLHEIGHT
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

    del APPLES[:]
    del APPLE_TIMES[:]
    SCORE = 0

    while True: # main game loop
        # update apples
        updateApples(wormCoords)

        # direction = handlePlayerInput(direction)
        direction = handleAgentInput(direction, wormCoords)

        dead_worms = []

        for i in range(len(wormCoords)):
            for wormBody in wormCoords[i][1:]:
                if wormBody['x'] == wormCoords[i][HEAD]['x'] and wormBody['y'] == wormCoords[i][HEAD]['y']:
                    if i not in dead_worms:
                        dead_worms.append(i)  # game over, worm 1's fault for hitting itself

            if wormCoords[i][HEAD]['x'] == -1 or wormCoords[i][HEAD]['x'] == CELLWIDTH or wormCoords[i][HEAD]['y'] == -1 or \
                    wormCoords[i][HEAD]['y'] == CELLHEIGHT:
                if i not in dead_worms:
                    dead_worms.append(i)

            for j in range(len(wormCoords)):
                if i == j:
                    pass
                elif wormCoords[i][HEAD] in wormCoords[j]:
                    if len(wormCoords[i]) > len(wormCoords[j]):
                        if i not in dead_worms:
                            dead_worms.append(i)
                    else:
                        if j not in dead_worms:
                            dead_worms.append(j)

            if len(wormCoords[i]) > MAX_WORM_LENGTH:
                if i not in dead_worms:
                    dead_worms.append(i)
                wormCoords.append([{'x': wormCoords[i][0]['x'], 'y': wormCoords[i][0]['y']},
                                  {'x': wormCoords[i][1]['x'], 'y': wormCoords[i][1]['y']},
                                  {'x': wormCoords[i][2]['x'], 'y': wormCoords[i][2]['y']}])

                wormCoords.append([{'x': wormCoords[i][6]['x'], 'y': wormCoords[i][6]['y']},
                                   {'x': wormCoords[i][7]['x'], 'y': wormCoords[i][7]['y']},
                                   {'x': wormCoords[i][8]['x'], 'y': wormCoords[i][8]['y']}])
                direction.append(direction[i])
                direction.append(direction[i])

        for i in dead_worms:
            del wormCoords[i]
            del direction[i]

        for i in range(len(wormCoords)):
            if direction[i] == UP:
                newHead = {'x': wormCoords[i][HEAD]['x'], 'y': wormCoords[i][HEAD]['y'] - 1}
            elif direction[i] == DOWN:
                newHead = {'x': wormCoords[i][HEAD]['x'], 'y': wormCoords[i][HEAD]['y'] + 1}
            elif direction[i] == LEFT:
                newHead = {'x': wormCoords[i][HEAD]['x'] - 1, 'y': wormCoords[i][HEAD]['y']}
            elif direction[i] == RIGHT:
                newHead = {'x': wormCoords[i][HEAD]['x'] + 1, 'y': wormCoords[i][HEAD]['y']}
            wormCoords[i].insert(0, newHead)

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorms(wormCoords)
        for apple in APPLES:
            drawApple(apple)
        drawScore()
        if len(wormCoords) <= 0:
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def updateApples(wormCoords):
    # check if worm has eaten an apply
    global SCORE
    genApples()

    for i in range(len(wormCoords)):
        APPLES[:] = [x for x in APPLES if not appleCollision(wormCoords[i], x)]
        if len(APPLES) < NUM_APPLES:
            SCORE += 1
        else:
            del wormCoords[i][-1]  # remove worm's tail segment
        genApples()

    for i in range(NUM_APPLES):
        APPLE_TIMES[i] -= 1
        if APPLE_TIMES[i] <= 0:
            del APPLES[i]
            del APPLE_TIMES[i]
            genApples()
            SCORE -= 1

def genApples():
    """Generates the apples with the following options:
    1. Uniformly distributed, infinite lifetime
    2. Uniformly distributed, short lifetime
    3. Uniformly distributed, variable lifetime
    4. Alternate between 1,2, and 3.
    5. Apples appear in a single quadrant.
    6. Apples appear in single quadrant, quadrant rotates over time
    7. Custom apple pattern that benefits centralized control"""
    if APPLE_OPTION == 1:
        genApplesOne()
    elif APPLE_OPTION == 2:
        genApplesTwo()
    elif APPLE_OPTION == 3:
        genApplesThree()
    elif APPLE_OPTION == 4:
        genApplesFour()
    elif APPLE_OPTION == 5:
        genApplesFive()
    elif APPLE_OPTION == 6:
        genApplesSix()
    elif APPLE_OPTION == 7:
        # genApplesSeven()
        pass
    else:
        print("Error: invalid genApples option")

def genApplesOne():
    while len(APPLES) < NUM_APPLES:
        APPLES.append(getRandomLocation())
        APPLE_TIMES.append(99999)

def genApplesTwo():
    while len(APPLES) < NUM_APPLES:
        APPLES.append(getRandomLocation())
        APPLE_TIMES.append(SHORT_TIME)

def genApplesThree():
    while len(APPLES) < NUM_APPLES:
        APPLES.append(getRandomLocation())
        APPLE_TIMES.append(random.randint(SHORT_TIME/3, SHORT_TIME*3))

def genApplesFour():
    global APPLE_OPTION_TIMER
    APPLE_OPTION_TIMER -= 1
    if APPLE_OPTION_TIMER <= 0:
        APPLE_OPTION_TIMER = 360
    if APPLE_OPTION_TIMER <= 120:
        genApplesThree()
    elif APPLE_OPTION_TIMER <= 240:
        genApplesTwo()
    else:
        genApplesOne()

def genApplesFive():
    while len(APPLES) < NUM_APPLES:
        APPLES.append(getRandomLocationQuadrant(APPLE_QUADRANT))
        APPLE_TIMES.append(SHORT_TIME)

def genApplesSix():
    global APPLE_OPTION_TIMER
    APPLE_OPTION_TIMER -= 1
    if APPLE_OPTION_TIMER <= 0:
        APPLE_OPTION_TIMER = 360
    if APPLE_OPTION_TIMER <= 90:
        while len(APPLES) < NUM_APPLES:
            APPLES.append(getRandomLocationQuadrant(1))
            APPLE_TIMES.append(SHORT_TIME)
    elif APPLE_OPTION_TIMER <= 180:
        while len(APPLES) < NUM_APPLES:
            APPLES.append(getRandomLocationQuadrant(2))
            APPLE_TIMES.append(SHORT_TIME)
    elif APPLE_OPTION_TIMER <= 270:
        while len(APPLES) < NUM_APPLES:
            APPLES.append(getRandomLocationQuadrant(3))
            APPLE_TIMES.append(SHORT_TIME)
    else:
        while len(APPLES) < NUM_APPLES:
            APPLES.append(getRandomLocationQuadrant(4))
            APPLE_TIMES.append(SHORT_TIME)

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

def getRandomLocationQuadrant(quadrant):
    if quadrant == 1:
        return {'x': random.randint(0, int(CELLWIDTH/2) - 1), 'y': random.randint(0, int(CELLHEIGHT/2) - 1)}
    elif quadrant == 2:
        return {'x': random.randint(int(CELLWIDTH/2) - 1, CELLWIDTH - 1), 'y': random.randint(0, int(CELLHEIGHT/2) - 1)}
    elif quadrant == 3:
        return {'x': random.randint(0, int(CELLWIDTH/2) - 1), 'y': random.randint(int(CELLHEIGHT/2) - 1, CELLHEIGHT -1)}
    else:
        return {'x': random.randint(int(CELLWIDTH/2) - 1, CELLWIDTH - 1), 'y': random.randint(int(CELLHEIGHT/2) - 1, CELLHEIGHT - 1)}

def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 100)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 100 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore():
    global SCORE
    scoreSurf = BASICFONT.render('Score: %s' % (SCORE), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 100, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawWorms(wormCoords):
    for i in range(len(wormCoords)):
        drawWorm(wormCoords[i], [DARKGREEN, GREEN])


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

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

def distance(x1, x2, y1, y2):
    return sqrt( (x2 - x1)**2 + (y2 - y1)**2 )

def findNearestApple(wormCoords):
    nearestApple = APPLES[0]
    shortest_dist = distance(wormCoords['x'],
                             nearestApple['x'],
                             wormCoords['y'],
                             nearestApple['y'])
    for apple in APPLES:
        dist = distance(wormCoords['x'],
                             apple['x'],
                             wormCoords['y'],
                             apple['y'])
        if dist <= MIN_APPLE_DISTANCE:
            if dist < shortest_dist:
                shortest_dist = dist
                nearestApple = apple

    if shortest_dist < MIN_APPLE_DISTANCE:
        return nearestApple

def findTargetDirection(target, wormCoords):
    # Move towards the target
    if target is not None:
        if target['x'] == wormCoords['x']:
            if target['y'] < wormCoords['y']:
                return UP
            else:
                return DOWN

    # avoid corners
    if wormCoords['x'] == 0 and wormCoords['y'] == 0:
        return DOWN
    if wormCoords['x'] == 0 and wormCoords['y'] == CELLHEIGHT - 1:
        return RIGHT
    if wormCoords['x'] == CELLWIDTH - 1 and wormCoords['y'] == 0:
        return LEFT
    if wormCoords['x'] == CELLWIDTH - 1 and wormCoords['y'] == CELLHEIGHT - 1:
        return UP
    # avoid walls
    if wormCoords['x'] == 0:
        return DOWN
    if wormCoords['x'] == CELLWIDTH - 1:
        return UP
    if wormCoords['y'] == 0:
        return RIGHT
    if wormCoords['y'] == CELLHEIGHT - 1:
        return LEFT

    if target is not None:
        if target['x'] < wormCoords['x']:
            return LEFT
    return RIGHT

def handleAgentInput(direction, wormCoords):
    for i in range(len(wormCoords)):
        target = findNearestApple(wormCoords[i][HEAD])
        temp_dir = findTargetDirection(target, wormCoords[i][HEAD])
        if temp_dir == UP and direction[i] == DOWN:
            pass
        elif temp_dir == RIGHT and direction[i] == LEFT:
            pass
        elif temp_dir == DOWN and direction[i] == UP:
            pass
        elif temp_dir == LEFT and direction[i] == RIGHT:
            pass
        else:
            direction[i] = temp_dir

    return direction

def handlePlayerInput(direction):
    for event in pygame.event.get():  # event handling loop
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

    return direction


if __name__ == '__main__':
    main()