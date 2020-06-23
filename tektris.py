#!/usr/bin/env python3

from tkinter import *
from enum import Enum
from math import ceil
import random

from tetrominos import *

BACKGROUND_COLOR = '#111111'
TEXT_COLOR = '#eeeeee'
GRID_COLOR = '#444444'

class GameState(Enum):
    READY, RUNNING, ANIMATING, PAUSED, LOST = range(5)

class TetrominoViewer:
    CELL_SIZE = 25

class Board(Canvas, TetrominoViewer):
    def __init__(self, master, width, height):
        super().__init__(master, width=width * self.CELL_SIZE,
                         height=height * self.CELL_SIZE,
                         background=BACKGROUND_COLOR)
        self.width = width
        self.height = height
        self.clear()

    def clear(self):
        self.delete(ALL)
        self.cells = [[None] * self.height for _ in range(self.width)]
        self.current = None
        self.current_ids = {}
        self.draw_grid()

    def draw_grid(self):
        for x in range(self.width):
            self.create_line((x+1) * self.CELL_SIZE, 0,
                             (x+1) * self.CELL_SIZE, self.height * self.CELL_SIZE,
                             fill=GRID_COLOR)

        for y in range(self.height):
            self.create_line(0, (y+1) * self.CELL_SIZE,
                             self.width * self.CELL_SIZE, (y+1) * self.CELL_SIZE,
                             fill=GRID_COLOR)

    def display(self, text):
        self.text_id = self.create_text(self.width * self.CELL_SIZE // 2,
                                        self.height * self.CELL_SIZE // 2,
                                        text=text, font=('Helvetica', 20, 'bold'),
                                        justify=CENTER, fill=TEXT_COLOR)

    def remove_text(self):
        self.delete(self.text_id)

    def set_current(self, piece):
        self.current = piece
        self.current.x = (self.width - piece.get_width()) // 2

        if not self.can_place():
            return False

        self.update_current()
        return True

    def update_current(self):
        for id in self.current_ids.values():
            self.delete(id)
        self.current_ids = self.current.draw(
            canvas=self, dx=self.current.x, dy=self.current.y, size=self.CELL_SIZE)

    def can_place(self):
        for cell in self.current:
            x = ceil(self.current.x + cell.x)
            y = ceil(self.current.y + cell.y)
            if x < 0 or x >= self.width or y < 0 or y >= self.height or self.cells[x][y]:
                return False
        return True

    def move_current(self, dx, dy):
        self.current.move(dx, dy)
        if self.can_place():
            self.update_current()
            return True
        else:
            self.current.move(-dx, -dy)
            return False

    def rotate_current(self):
        self.current.rotate()
        if self.can_place():
            self.update_current()
            return True
        else:
            self.current.rotate(-1)
            return False

    def lock_current(self):
        for cell in self.current:
            x = ceil(self.current.x + cell.x)
            y = ceil(self.current.y + cell.y)
            self.cells[x][y] = self.current_ids[cell]
        self.current = None
        self.current_ids = {}

    def remove_complete_lines(self):
        completed = 0
        for y in range(self.height):
            if all(self.cells[x][y] for x in range(self.width)):
                completed += 1
                for x in range(self.width):
                    self.delete(self.cells[x][y])
                    for l in range(y, 0, -1):
                        self.cells[x][l] = self.cells[x][l - 1]
                        self.cells[x][0] = None
                        if self.cells[x][l]:
                            self.move(self.cells[x][l], 0, self.CELL_SIZE)
        return completed
            

class Previewer(Canvas, TetrominoViewer):
    WIDTH = 5
    HEIGHT = 5

    def __init__(self, master):
        super().__init__(master, width=self.CELL_SIZE * self.WIDTH,
                         height=self.CELL_SIZE * self.HEIGHT,
                         background=BACKGROUND_COLOR)

    def set_current(self, piece):
        self.delete(ALL)
        dx = (self.WIDTH - piece.get_width()) / 2
        dy = (self.HEIGHT - piece.get_height()) / 2
        piece.draw(canvas=self, dx=dx, dy=dy, size=self.CELL_SIZE)

class KeyRepeatHandler:
    FIRST_REPEAT_DELAY = 250
    REPEAT_INTERVAL = 15

    def __init__(self, widget, handler):
        widget.bind('<KeyPress>', self.key_press)
        widget.bind('<KeyRelease>', self.key_release)
        self.widget = widget
        self.handler = handler
        self.after_id = None

    def key_release(self, event):
        if self.after_id != None:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

    def key_press(self, event):
        if not self.after_id:
            self.after_id = self.widget.after_idle(self.key_start, event)

    def key_start(self, event):
        self.key_handle(event)
        self.after_id = self.widget.after(self.FIRST_REPEAT_DELAY, self.key_repeat, event)

    def key_repeat(self, event):
        self.key_handle(event)
        self.after_id = self.widget.after(self.REPEAT_INTERVAL, self.key_repeat, event)

    def key_handle(self, event):
        self.handler(event)

class Game(Tk):
    TETROMINOS = (TetrominoT, TetrominoI, TetrominoL, TetrominoJ, TetrominoS, TetrominoZ, TetrominoO)

    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        self.title('TeKtris')

        frame = Frame(self, bd=10, relief=SUNKEN, background=BACKGROUND_COLOR)
        frame.pack(side=LEFT)
        self.board = Board(frame, 10, 20)
        self.board.pack()

        frame = Frame(self, bd=10, relief=SUNKEN, background=BACKGROUND_COLOR)
        frame.pack(side=TOP)
        self.previewer = Previewer(frame)
        self.previewer.pack()

        frame = Frame(self, bd=10, relief=SUNKEN, background=BACKGROUND_COLOR)
        frame.pack(side=TOP, expand=YES, fill=BOTH)
        Label(frame, text='LEVEL', font=('Helvetica', 20, 'bold'), fg=TEXT_COLOR, background=BACKGROUND_COLOR).pack(expand=YES)
        self.label_level = Label(frame, text='0', font=('Helvetica', 20, 'bold'), fg=TEXT_COLOR, background=BACKGROUND_COLOR)
        self.label_level.pack(expand=YES)
        Label(frame, text='LINES', font=('Helvetica', 20, 'bold'), fg=TEXT_COLOR, background=BACKGROUND_COLOR).pack(expand=YES)
        self.label_lines = Label(frame, text='0', font=('Helvetica', 20, 'bold'), fg=TEXT_COLOR, background=BACKGROUND_COLOR)
        self.label_lines.pack(expand=YES)
        Label(frame, text='SCORE', font=('Helvetica', 20, 'bold'), fg=TEXT_COLOR, background=BACKGROUND_COLOR).pack(expand=YES)
        self.label_score = Label(frame, text='0', font=('Helvetica', 20, 'bold'), fg=TEXT_COLOR, background=BACKGROUND_COLOR)
        self.label_score.pack(expand=YES)

        self.key_repeat_handler = KeyRepeatHandler(self, self.handle_key)

        self.start()

        self.after(self.drop_interval(), self.gameloop)

    def handle_key(self, event):
        if self.state == GameState.READY:
            self.start_game()
            return

        if event.char == 'q':
            self.destroy()
        elif event.char == 'p':
            self.pause()
        elif event.char == 'r':
            self.restart()
        elif event.keysym == 'Left':
            self.left()
        elif event.keysym == 'Right':
            self.right()
        elif event.keysym == 'Up':
            self.rotate()
        elif event.keysym == 'Down':
            self.drop()
        elif event.keysym == 'space':
            self.hard_drop()

    def update_labels(self):
        self.label_level['text'] = str(self.level)
        self.label_lines['text'] = str(self.lines)
        self.label_score['text'] = str(self.score)

    def start(self):
        self.state = GameState.READY

        self.board.clear()
        self.board.display('Press any key\nto start')
        self.level = 1
        self.lines = 0
        self.score = 0

        self.update_labels()

        tetromino = random.choice(self.TETROMINOS)
        self.next = tetromino()
        self.pick_next()

    def start_game(self):
        self.state = GameState.RUNNING
        self.board.remove_text()

    def restart(self):
        if self.state != GameState.LOST:
            return
        self.start()

    def pause(self):
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
        else:
            return

        if self.state == GameState.RUNNING:
            self.board.remove_text()
        else:
            self.board.display('PAUSE')
        
    def pick_next(self):
        if not self.board.set_current(self.next):
            return False

        tetromino = random.choice(self.TETROMINOS)
        self.next = tetromino()
        self.previewer.set_current(self.next)
        return True

    def left(self):
        if self.state != GameState.RUNNING:
            return
        self.board.move_current(-1, 0)

    def right(self):
        if self.state != GameState.RUNNING:
            return
        self.board.move_current(1, 0)

    def rotate(self):
        if self.state != GameState.RUNNING:
            return
        self.board.rotate_current()

    def drop(self):
        if self.state != GameState.RUNNING:
            return

        if not self.board.move_current(0, 1):
            self.board.lock_current()

        self.post_drop()

    def hard_drop(self):
        if self.state != GameState.RUNNING:
            return

        self.state = GameState.ANIMATING
        self.animationloop()

    def post_drop(self):
        completed = self.board.remove_complete_lines()
        self.lines += completed
        POINTS = (40, 100, 300, 1200)
        if completed > 0:
            self.score += (self.level + 1) * POINTS[completed - 1]

        self.level = min(10, 1 + self.lines // 10)

        self.update_labels()

        if not self.board.current:
            if not self.pick_next():
                self.state = GameState.LOST
                self.board.display('GAME OVER')

    def animationloop(self):
        if not self.board.move_current(0, 0.5):
            self.board.lock_current()
            self.state = GameState.RUNNING
            self.post_drop()
        else:
            self.after(5, self.animationloop)

    def drop_interval(self):
        return (11 - self.level) * 50

    def gameloop(self):
        self.drop()
        self.after(self.drop_interval(), self.gameloop)

game = Game()
game.mainloop()

