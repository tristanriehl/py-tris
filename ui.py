import pygame
from engine import COLORS, TETROMINOES, BOARD_WIDTH, VISIBLE_HEIGHT

CELL_SIZE = 30
GRID_OFFSET_X = 220
GRID_OFFSET_Y = 50
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700

BACKGROUND_COLOR = (18, 18, 24)
GRID_LINE_COLOR = (35, 35, 45)
BORDER_COLOR = (60, 60, 80)

class Renderer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("TETR.IO Modular Practice Engine")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.font = pygame.font.SysFont("Helvetica", 18)
        self.title_font = pygame.font.SysFont("Helvetica", 22, bold=True)

    def render(self, engine, config):
        self.screen.fill(BACKGROUND_COLOR)

        self._draw_board(engine)
        self._draw_hold(engine)
        self._draw_queue(engine)
        self._draw_info_overlay(config)

        pygame.display.flip()

    def _draw_board(self, engine):
        # Board container
        board_rect = pygame.Rect(
            GRID_OFFSET_X, GRID_OFFSET_Y,
            BOARD_WIDTH * CELL_SIZE, VISIBLE_HEIGHT * CELL_SIZE
        )
        pygame.draw.rect(self.screen, (10, 10, 15), board_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, board_rect, 2)

        # Draw grid lines
        for x in range(BOARD_WIDTH + 1):
            px = GRID_OFFSET_X + x * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (px, GRID_OFFSET_Y), (px, GRID_OFFSET_Y + VISIBLE_HEIGHT * CELL_SIZE))
        for y in range(VISIBLE_HEIGHT + 1):
            py = GRID_OFFSET_Y + y * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (GRID_OFFSET_X, py), (GRID_OFFSET_X + BOARD_WIDTH * CELL_SIZE, py))

        # Render stack
        for r in range(20, 40):
            for c in range(BOARD_WIDTH):
                piece_type = engine.board[r][c]
                if piece_type:
                    color = COLORS.get(piece_type, (150, 150, 150))
                    self._draw_cell(c, r - 20, color)

        # Render active piece & ghost
        if engine.active_piece and not engine.game_over:
            # Ghost piece
            ghost_y = engine.get_ghost_y()
            ghost_color = tuple(int(c * 0.3) for c in COLORS[engine.active_piece.type])
            for bx, by in engine.active_piece.get_blocks(y=ghost_y):
                if by >= 20:
                    self._draw_cell(bx, by - 20, ghost_color, border_only=True)

            # Active piece
            active_color = COLORS[engine.active_piece.type]
            for bx, by in engine.active_piece.get_blocks():
                if by >= 20:
                    self._draw_cell(bx, by - 20, active_color)

    def _draw_cell(self, grid_x, grid_y, color, border_only=False):
        px = GRID_OFFSET_X + grid_x * CELL_SIZE
        py = GRID_OFFSET_Y + grid_y * CELL_SIZE
        rect = pygame.Rect(px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2)

        if border_only:
            pygame.draw.rect(self.screen, color, rect, 2)
        else:
            pygame.draw.rect(self.screen, color, rect, border_radius=3)

    def _draw_hold(self, engine):
        box_rect = pygame.Rect(50, GRID_OFFSET_Y, 130, 120)
        pygame.draw.rect(self.screen, (10, 10, 15), box_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, box_rect, 2)

        txt = self.title_font.render("HOLD", True, (200, 200, 200))
        self.screen.blit(txt, (box_rect.x + 10, box_rect.y + 10))

        if engine.hold_piece:
            color = COLORS[engine.hold_piece] if engine.can_hold else (100, 100, 100)
            blocks = TETROMINOES[engine.hold_piece][0]
            for bx, by in blocks:
                px = box_rect.x + 30 + bx * 20
                py = box_rect.y + 50 + by * 20
                pygame.draw.rect(self.screen, color, (px, py, 18, 18), border_radius=2)

    def _draw_queue(self, engine):
        box_rect = pygame.Rect(540, GRID_OFFSET_Y, 130, 420)
        pygame.draw.rect(self.screen, (10, 10, 15), box_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, box_rect, 2)

        txt = self.title_font.render("NEXT", True, (200, 200, 200))
        self.screen.blit(txt, (box_rect.x + 10, box_rect.y + 10))

        for i in range(min(5, len(engine.queue))):
            piece_type = engine.queue[i]
            color = COLORS[piece_type]
            blocks = TETROMINOES[piece_type][0]
            for bx, by in blocks:
                px = box_rect.x + 30 + bx * 18
                py = box_rect.y + 50 + i * 70 + by * 18
                pygame.draw.rect(self.screen, color, (px, py, 16, 16), border_radius=2)

    def _draw_info_overlay(self, config):
        handling = config.get("handling", {})
        info = [
            f"DAS: {handling.get('das_ms')} ms",
            f"ARR: {handling.get('arr_ms')} ms",
            f"SDF: {handling.get('sdf')}x",
            "",
            "[R] Reset Board",
            "[I] Import Board (test.png)",
        ]
        y = 200
        for line in info:
            txt = self.font.render(line, True, (160, 160, 180))
            self.screen.blit(txt, (50, y))
            y += 24
