"""
recommended:
sudo aptitude install fonts-noto-color-emoji
urxvt -fg white -bg black -fn "xft:Noto Color Emoji 20"
"""

import time
import random
import math
import urwid

width, height = 20, 20

x, y = 10, 10
ex, ey = 2, 3
eWins = 0
playerWins = 0
lastEnemyStep = 0
boardSetup = 0
runAwaySteps = 0
traps = [
    # x, y, placetime
]

def chase():
    global ex, ey, lastEnemyStep
    now = time.time()
    ePeriod = max(.1, 1 - playerWins * .2)
    if now < lastEnemyStep + ePeriod:
        return
    lastEnemyStep = now

    dx = random.choice([-1, 0, 1])
    dy = random.choice([-1, 0, 1])
    if random.random() < .5:
        dx = 1 if x > ex else -1
        dy = 1 if y > ey else -1

    ex = ex + dx
    ey = ey + dy

def trapEnemy():
    global playerWins
    playerWins = playerWins + 1
    resetBoard("Dog fell in a trap")

def enemyHits():
    global eWins
    eWins = eWins + 1
    resetBoard("Dog catches you")
    
def trapPlayer():
    global eWins
    eWins = eWins + 1
    resetBoard("You fell in a trap")

def resetBoard(message):
    global boardSetup, x, y, ex, ey
    footer.set_text(message)
    boardSetup = 0
    x = random.randrange(width)
    y = random.randrange(height // 2)
    ex = random.randrange(width)
    ey = random.randrange(height // 2 - 5) + height // 2 + 5
    traps[:] = []

def stepAway():
    global x, y
    allowed = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) != (x, y) and (nx, ny) != (ex, ey):
                allowed.append((nx, ny))

    random.shuffle(allowed)
    for nx, ny in allowed:
        if getTrap(nx, ny) is None:
            x,  y = nx, ny
            return
    
    # they all have traps- you're stuck, so just sit on the trap you placed and lose

def getTrap(qx, qy):
    for tx, ty, placed in traps:
        if (tx, ty) == (qx, qy):
            return placed
    return None
    

def draw():
    now = time.time()
    out = ""
    rnd = random.Random(36)
    if (x, y) == (ex, ey):
        enemyHits()
    for by in range(height):
        outRow = ""
        for bx in range(width):
            cell = rnd.choice("abcdefghijklmnopqrsuvwxyz")+' '
            if boardSetup is not None:
                dist = math.hypot(bx - width / 2, by - height / 2) / width / 2
                if dist > boardSetup:
                    cell = '  '
            trap = getTrap(bx, by)
            if (bx, by) == (x, y):
                cell = "😲"
                if trap is not None:
                    trapPlayer()
            if (bx, by) == (ex, ey):
                cell = "🐕"
                if trap is not None:
                    trapEnemy()
            
            if trap is not None:
                age = now - trap
                if age > .5:
                    cell = 't '
                else:
                    cell = 'T '

            outRow = outRow + cell
        out = out + outRow + "\n"
    return out


def update(loop, _):
    global boardSetup, runAwaySteps
    chase()
    txt.set_text(draw())
    if runAwaySteps > 0:
        stepAway()
        runAwaySteps = runAwaySteps - 1
    if boardSetup is not None:
        boardSetup = boardSetup + .03
        if boardSetup >= 1:
            boardSetup = None
            footer.set_text(f'dog: {eWins}   you: {playerWins}')

    loop.set_alarm_in(.05, update)

def onKey(key):
    global x, y
    if key == 'left':
        x = max(x - 1, 0)
    if key == 'right':
        x = min(x + 1, width - 1)
    if key == 'up':
        y = max(y - 1, 0)
    if key == 'down':
        y = min(y + 1, height - 1)
    if key == ' ':
        traps.append((x, y, time.time()))
        runAwaySteps = 3
        stepAway()

txt = urwid.Text("")
fill = urwid.Filler(txt, valign=urwid.TOP)
title = urwid.Text("traps game - arrow keys move; space to set a trap")
footer = urwid.Text("")
frame = urwid.Frame(fill, header=title, footer=footer)

resetBoard("starting")

loop = urwid.MainLoop(frame, unhandled_input=onKey)
update(loop, None)
loop.run()