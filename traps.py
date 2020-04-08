import time
import random
import math
import urwid


class Game:
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
    now = time.time()
    ePeriod = max(.1, 1 - Game.playerWins * .2)
    if now < Game.lastEnemyStep + ePeriod:
        return
    Game.lastEnemyStep = now

    dx = random.choice([-1, 0, 1])
    dy = random.choice([-1, 0, 1])
    if random.random() < .5:
        dx = 1 if Game.x > Game.ex else -1
        dy = 1 if Game.y > Game.ey else -1

    Game.ex = Game.ex + dx
    Game.ey = Game.ey + dy


def trapEnemy():
    Game.playerWins = Game.playerWins + 1
    resetBoard("Dog fell in a trap")


def enemyHits():
    Game.eWins = Game.eWins + 1
    resetBoard("Dog catches you")


def trapPlayer():
    Game.eWins = Game.eWins + 1
    resetBoard("You fell in a trap")


def resetBoard(message):
    footer.set_text(message)
    Game.boardSetup = 0
    Game.x = random.randrange(Game.width)
    Game.y = random.randrange(Game.height // 2)
    Game.ex = random.randrange(Game.width)
    Game.ey = random.randrange(Game.height // 2 - 5) + Game.height // 2 + 5
    Game.traps[:] = []


def stepAway():
    allowed = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = Game.x + dx, Game.y + dy
            if 0 <= nx < Game.width and 0 <= ny < Game.height and (nx, ny) != (
                    Game.x, Game.y) and (nx, ny) != (Game.ex, Game.ey):
                allowed.append((nx, ny))

    random.shuffle(allowed)
    for nx, ny in allowed:
        if getTrap(nx, ny) is None:
            Game.x, Game.y = nx, ny
            return

    # they all have traps- you're stuck, so just sit on the trap you placed
    # and lose


def getTrap(qx, qy):
    for tx, ty, placed in Game.traps:
        if (tx, ty) == (qx, qy):
            return placed
    return None


def draw():
    now = time.time()
    out = ""
    rnd = random.Random(36)
    if (Game.x, Game.y) == (Game.ex, Game.ey):
        enemyHits()
    for by in range(Game.height):
        outRow = ""
        for bx in range(Game.width):
            cell = rnd.choice("abcdefghijklmnopqrsuvwxyz") + ' '
            if Game.boardSetup is not None:
                dist = math.hypot(bx - Game.width / 2,
                                  by - Game.height / 2) / Game.width / 2
                if dist > Game.boardSetup:
                    cell = '  '
            trap = getTrap(bx, by)
            if (bx, by) == (Game.x, Game.y):
                cell = "😲"
                if trap is not None:
                    trapPlayer()
            if (bx, by) == (Game.ex, Game.ey):
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
    chase()
    txt.set_text(draw())
    if Game.runAwaySteps > 0:
        stepAway()
        Game.runAwaySteps = Game.runAwaySteps - 1
    if Game.boardSetup is not None:
        Game.boardSetup = Game.boardSetup + .03
        if Game.boardSetup >= 1:
            Game.boardSetup = None
            footer.set_text(f'dog: {Game.eWins}   you: {Game.playerWins}')

    loop.set_alarm_in(.05, update)


def onKey(key):
    if key == 'left':
        Game.x = max(Game.x - 1, 0)
    if key == 'right':
        Game.x = min(Game.x + 1, Game.width - 1)
    if key == 'up':
        Game.y = max(Game.y - 1, 0)
    if key == 'down':
        Game.y = min(Game.y + 1, Game.height - 1)
    if key == ' ':
        Game.traps.append((Game.x, Game.y, time.time()))
        Game.runAwaySteps = 3
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
