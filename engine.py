import random
import copy

BOARD_WIDTH = 10
BOARD_HEIGHT = 40
VISIBLE_HEIGHT = 20

# Tetromino shapes in 4x4 or 3x3 matrices facing North (0)
# Orientations: 0=N, 1=E, 2=S, 3=W
TETROMINOES = {
    'I': [
        [(0,1), (1,1), (2,1), (3,1)],
        [(2,0), (2,1), (2,2), (2,3)],
        [(0,2), (1,2), (2,2), (3,2)],
        [(1,0), (1,1), (1,2), (1,3)]
    ],
    'J': [
        [(0,0), (0,1), (1,1), (2,1)],
        [(1,0), (2,0), (1,1), (1,2)],
        [(0,1), (1,1), (2,1), (2,2)],
        [(1,0), (1,1), (0,2), (1,2)]
    ],
    'L': [
        [(2,0), (0,1), (1,1), (2,1)],
        [(1,0), (1,1), (1,2), (2,2)],
        [(0,1), (1,1), (2,1), (0,2)],
        [(0,0), (1,0), (1,1), (1,2)]
    ],
    'O': [
        [(1,0), (2,0), (1,1), (2,1)],
        [(1,0), (2,0), (1,1), (2,1)],
        [(1,0), (2,0), (1,1), (2,1)],
        [(1,0), (2,0), (1,1), (2,1)]
    ],
    'S': [
        [(1,0), (2,0), (0,1), (1,1)],
        [(1,0), (1,1), (2,1), (2,2)],
        [(1,1), (2,1), (0,2), (1,2)],
        [(0,0), (0,1), (1,1), (1,2)]
    ],
    'T': [
        [(1,0), (0,1), (1,1), (2,1)],
        [(1,0), (1,1), (2,1), (1,2)],
        [(0,1), (1,1), (2,1), (1,2)],
        [(1,0), (0,1), (1,1), (1,2)]
    ],
    'Z': [
        [(0,0), (1,0), (1,1), (2,1)],
        [(2,0), (1,1), (2,1), (1,2)],
        [(0,1), (1,1), (1,2), (2,2)],
        [(1,0), (0,1), (1,1), (0,2)]
    ]
}

# Colors matching standard Modern Guidelines / TETR.IO RGB
COLORS = {
    'I': (0, 240, 240),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
    'O': (240, 240, 0),
    'S': (0, 240, 0),
    'T': (160, 0, 240),
    'Z': (240, 0, 0),
    'G': (128, 128, 128)  # Solid stack / garbage
}

# Standard SRS Kick Tables (dx, dy) where +x is right, +y is UP in SRS (converted in code to grid coords)
JLSZGT_KICKS = {
    (0, 1): [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)],
    (1, 0): [(0,0), (1,0), (1,-1), (0,2), (1,2)],
    (1, 2): [(0,0), (1,0), (1,-1), (0,2), (1,2)],
    (2, 1): [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)],
    (2, 3): [(0,0), (1,0), (1,1), (0,-2), (1,-2)],
    (3, 2): [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)],
    (3, 0): [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)],
    (0, 3): [(0,0), (1,0), (1,1), (0,-2), (1,-2)],
    # 180 rotations
    (0, 2): [(0,0), (0,1), (1,1), (-1,1), (1,0), (-1,0)],
    (2, 0): [(0,0), (0,-1), (-1,-1), (1,-1), (-1,0), (1,0)],
    (1, 3): [(0,0), (1,0), (1,2), (1,1), (0,1), (0,2)],
    (3, 1): [(0,0), (-1,0), (-1,2), (-1,1), (0,1), (0,2)]
}

I_KICKS = {
    (0, 1): [(0,0), (-2,0), (1,0), (-2,-1), (1,2)],
    (1, 0): [(0,0), (2,0), (-1,0), (2,1), (-1,-2)],
    (1, 2): [(0,0), (-1,0), (2,0), (-1,2), (2,-1)],
    (2, 1): [(0,0), (1,0), (-2,0), (1,-2), (-2,1)],
    (2, 3): [(0,0), (2,0), (-1,0), (2,1), (-1,-2)],
    (3, 2): [(0,0), (-2,0), (1,0), (-2,-1), (1,2)],
    (3, 0): [(0,0), (1,0), (-2,0), (1,-2), (-2,1)],
    (0, 3): [(0,0), (-1,0), (2,0), (-1,2), (2,-1)],
    # 180 rotations
    (0, 2): [(0,0), (-1,0), (2,0), (-1,1), (2,-1)],
    (2, 0): [(0,0), (1,0), (-2,0), (1,-1), (-2,1)],
    (1, 3): [(0,0), (0,1), (0,-2), (1,1), (-1,-2)],
    (3, 1): [(0,0), (0,-1), (0,2), (-1,-1), (1,2)]
}

class Tetromino:
    def __init__(self, shape_type):
        self.type = shape_type
        self.orient = 0  # 0: N, 1: E, 2: S, 3: W
        self.x = 3       # Initial spawn X
        self.y = 18      # Initial spawn Y (near top of visible grid)

    def get_blocks(self, orient=None, x=None, y=None):
        if orient is None: orient = self.orient
        if x is None: x = self.x
        if y is None: y = self.y
        local_blocks = TETROMINOES[self.type][orient]
        return [(x + bx, y + by) for bx, by in local_blocks]

class TetrisEngine:
    def __init__(self, lock_delay_ms=500.0, max_lock_resets=15):
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.bag = []
        self.queue = []
        self.hold_piece = None
        self.can_hold = True
        self.active_piece = None
        
        self.lock_delay_ms = lock_delay_ms
        self.max_lock_resets = max_lock_resets
        self.lock_timer = 0.0
        self.lock_resets = 0
        self.is_grounded = False
        self.game_over = False

        self._refill_queue()
        self.spawn_piece()

    def _refill_queue(self):
        while len(self.queue) < 7:
            if not self.bag:
                self.bag = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
                random.shuffle(self.bag)
            self.queue.append(self.bag.pop(0))

    def spawn_piece(self, piece_type=None):
        if piece_type is None:
            self._refill_queue()
            piece_type = self.queue.pop(0)
            self._refill_queue()

        self.active_piece = Tetromino(piece_type)
        self.can_hold = True
        self.lock_timer = 0.0
        self.lock_resets = 0
        self.is_grounded = False

        if not self._is_valid_position(self.active_piece):
            self.game_over = True

    def _is_valid_position(self, piece, orient=None, x=None, y=None):
        blocks = piece.get_blocks(orient, x, y)
        for bx, by in blocks:
            if bx < 0 or bx >= BOARD_WIDTH or by < 0 or by >= BOARD_HEIGHT:
                return False
            if self.board[by][bx] is not None:
                return False
        return True

    def update(self, dt_ms):
        if not self.active_piece or self.game_over:
            return

        # Check if piece is touching ground
        if not self._is_valid_position(self.active_piece, y=self.active_piece.y + 1):
            if not self.is_grounded:
                self.is_grounded = True
                self.lock_timer = 0.0

            self.lock_timer += dt_ms
            if self.lock_timer >= self.lock_delay_ms:
                self.lock_piece()
        else:
            self.is_grounded = False
            self.lock_timer = 0.0

    def reset_lock_delay(self):
        if self.is_grounded:
            if self.lock_resets < self.max_lock_resets:
                self.lock_timer = 0.0
                self.lock_resets += 1

    def move_left(self):
        if self.active_piece and self._is_valid_position(self.active_piece, x=self.active_piece.x - 1):
            self.active_piece.x -= 1
            self.reset_lock_delay()
            return True
        return False

    def move_right(self):
        if self.active_piece and self._is_valid_position(self.active_piece, x=self.active_piece.x + 1):
            self.active_piece.x += 1
            self.reset_lock_delay()
            return True
        return False

    def soft_drop(self):
        if self.active_piece and self._is_valid_position(self.active_piece, y=self.active_piece.y + 1):
            self.active_piece.y += 1
            return True
        return False

    def hard_drop(self):
        if not self.active_piece or self.game_over:
            return
        while self._is_valid_position(self.active_piece, y=self.active_piece.y + 1):
            self.active_piece.y += 1
        self.lock_piece()

    def rotate(self, rotation_type):
        """
        rotation_type: 'CW' (1 step), 'CCW' (3 steps), '180' (2 steps)
        """
        if not self.active_piece or self.game_over:
            return False

        old_orient = self.active_piece.orient
        steps = 1 if rotation_type == 'CW' else (3 if rotation_type == 'CCW' else 2)
        new_orient = (old_orient + steps) % 4

        kick_table = I_KICKS if self.active_piece.type == 'I' else JLSZGT_KICKS
        kick_key = (old_orient, new_orient)
        kicks = kick_table.get(kick_key, [(0, 0)])

        for dx, dy in kicks:
            # SRS dy is +Up, so in screen coords (+Down) dy becomes -dy
            test_x = self.active_piece.x + dx
            test_y = self.active_piece.y - dy
            if self._is_valid_position(self.active_piece, orient=new_orient, x=test_x, y=test_y):
                self.active_piece.orient = new_orient
                self.active_piece.x = test_x
                self.active_piece.y = test_y
                self.reset_lock_delay()
                return True
        return False

    def hold(self):
        if not self.can_hold or not self.active_piece or self.game_over:
            return

        curr_type = self.active_piece.type
        if self.hold_piece is None:
            self.hold_piece = curr_type
            self.spawn_piece()
        else:
            self.hold_piece, curr_type = curr_type, self.hold_piece
            self.spawn_piece(curr_type)

        self.can_hold = False

    def lock_piece(self):
        for bx, by in self.active_piece.get_blocks():
            if 0 <= bx < BOARD_WIDTH and 0 <= by < BOARD_HEIGHT:
                self.board[by][bx] = self.active_piece.type

        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        lines_to_clear = [r for r in range(BOARD_HEIGHT) if all(self.board[r][c] is not None for c in range(BOARD_WIDTH))]
        for r in lines_to_clear:
            del self.board[r]
            self.board.insert(0, [None for _ in range(BOARD_WIDTH)])

    def get_ghost_y(self):
        if not self.active_piece:
            return 0
        ghost_y = self.active_piece.y
        while self._is_valid_position(self.active_piece, y=ghost_y + 1):
            ghost_y += 1
        return ghost_y

    def reset_board(self):
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.bag = []
        self.queue = []
        self.hold_piece = None
        self.can_hold = True
        self.game_over = False
        self._refill_queue()
        self.spawn_piece()
