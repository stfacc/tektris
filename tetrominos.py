from collections import namedtuple

__all__ = [ 'TetrominoT', 'TetrominoI', 'TetrominoL', 'TetrominoJ', 'TetrominoS', 'TetrominoZ', 'TetrominoO' ]

Cell = namedtuple('Cell', 'x y')

PALETTES = (
    ('blue', 'red', 'yellow', 'orange', 'purple', 'green', 'cyan'),
    ('#54c7fc', '#ffcd00', '#ff9600', '#ff2851', '#0076ff', '#44db5e', '#ff3824'),
    ('#00b3ca', '#7dd0b6', '#1d4e89', '#d2b29b', '#e38690', '#f69256', '#eaf98b'),
    ('#02a68d', '#016295', '#c8cd7d', '#44225e', '#bb1e39', '#e4633b', '#ba1a62'),
    ('#6db875', '#dd7983', '#0f5959', '#17a697', '#638ca6', '#b569b3', '#d93240')
)

PALETTE = PALETTES[-1]

class Tetromino:
    def __init__(self):
        self.state = 0
        self.x = 0
        self.y = 0

    def get_width(self):
        shape = self.SHAPES[self.state]
        return max(len(line) for line in shape.split())

    def get_height(self):
        shape = self.SHAPES[self.state]
        return len(shape.split())

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self, n=1):
        self.state = (self.state + n) % len(self.SHAPES)

    def draw(self, canvas, dx, dy, size):
        ids = {}
        for cell in self:
            x = cell.x + dx 
            y = cell.y + dy
            ids[cell] = canvas.create_rectangle(x * size,  y * size,
                                                (x + 1) * size, (y + 1) * size,
                                                fill=self.COLOR, outline='#eeeeee')
        return ids


    def __iter__(self):
        shape = self.SHAPES[self.state]
        for y, line in enumerate(shape.split()):
            for x, c in enumerate(line):
                if c != '.':
                    yield Cell(x, y)

class TetrominoL(Tetromino):
    COLOR = PALETTE[0]
    SHAPES = (
"""
xxx
x..
""",
"""
xx
.x
.x
""",
"""
..x
xxx
""",
"""
x.
x.
xx
"""
)

class TetrominoJ(Tetromino):
    COLOR = PALETTE[1]
    SHAPES = (
"""
xxx
..x
""",
"""
.x
.x
xx
""",
"""
x..
xxx
""",
"""
xx
x.
x.
"""
)

class TetrominoS(Tetromino):
    COLOR = PALETTE[2]
    SHAPES = (
"""
.xx
xx.
""",
"""
x.
xx
.x
"""
)

class TetrominoZ(Tetromino):
    COLOR = PALETTE[3]
    SHAPES = (
"""
xx.
.xx
""",
"""
.x
xx
x.
"""
)

class TetrominoT(Tetromino):
    COLOR = PALETTE[4]
    SHAPES = (
"""
xxx
.x.
""",
"""
.x
xx
.x
""",
"""
.x.
xxx
""",
"""
x.
xx
x.
""")

class TetrominoO(Tetromino):
    COLOR = PALETTE[5]
    SHAPES = (
"""
xx
xx
""",
)

class TetrominoI(Tetromino):
    COLOR = PALETTE[6]
    SHAPES = (
"""
xxxx
""",
"""
.x
.x
.x
.x
"""
)

