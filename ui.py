import pygame
from engine import COLORS, TETROMINOES, BOARD_WIDTH, VISIBLE_HEIGHT

from input import SETTINGS_ITEMS

CELL_SIZE = 30
GRID_OFFSET_X = 220
GRID_OFFSET_Y = 50
WINDOW_WIDTH = 690
WINDOW_HEIGHT = 700

BACKGROUND_COLOR = (18, 18, 24)
GRID_LINE_COLOR = (35, 35, 45)
BORDER_COLOR = (60, 60, 80)

class Renderer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("TETR.IO Modular Practice Engine")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        self.font = pygame.font.SysFont("Helvetica", 15)
        self.title_font = pygame.font.SysFont("Helvetica", 20, bold=True)

    def render(self, engine, config, input_handler=None):
        self.screen.fill(BACKGROUND_COLOR)

        self._draw_board(engine)
        self._draw_hold(engine)
        self._draw_queue(engine, input_handler)
        self._draw_info_overlay(config)
        self._draw_palette(input_handler)
        self._draw_settings_panel(config, input_handler)

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

    def _draw_queue(self, engine, input_handler=None):
        box_rect = pygame.Rect(540, GRID_OFFSET_Y, 130, 420)
        pygame.draw.rect(self.screen, (10, 10, 15), box_rect, border_radius=6)

        in_queue_input = input_handler.in_queue_input if input_handler else False
        border_col = (240, 200, 0) if in_queue_input else BORDER_COLOR
        pygame.draw.rect(self.screen, border_col, box_rect, 2, border_radius=6)

        title_str = "NEXT (TYPING)" if in_queue_input else "NEXT [Q]"
        txt = self.title_font.render(title_str, True, (240, 200, 0) if in_queue_input else (200, 200, 200))
        self.screen.blit(txt, (box_rect.x + 10, box_rect.y + 10))

        # Active Queue Input Text Box Indicator
        if in_queue_input:
            input_box = pygame.Rect(box_rect.x + 8, box_rect.y + 36, 114, 24)
            pygame.draw.rect(self.screen, (30, 35, 45), input_box, border_radius=4)
            pygame.draw.rect(self.screen, (240, 200, 0), input_box, 1, border_radius=4)
            q_str = "".join(engine.queue[-7:]) + "_"
            q_txt = self.font.render(q_str, True, (255, 220, 100))
            self.screen.blit(q_txt, (input_box.x + 5, input_box.y + 3))

        start_y = 65 if in_queue_input else 45
        for i in range(min(5, len(engine.queue))):
            piece_type = engine.queue[i]
            color = COLORS[piece_type]
            blocks = TETROMINOES[piece_type][0]
            slot_rect = pygame.Rect(box_rect.x + 10, box_rect.y + start_y + i * 68, 110, 62)
            pygame.draw.rect(self.screen, (20, 22, 30), slot_rect, border_radius=4)
            pygame.draw.rect(self.screen, (40, 40, 55), slot_rect, 1, border_radius=4)
            for bx, by in blocks:
                px = slot_rect.x + 25 + bx * 18
                py = slot_rect.y + 10 + by * 18
                pygame.draw.rect(self.screen, color, (px, py, 16, 16), border_radius=2)

    def _draw_info_overlay(self, config):
        handling = config.get("handling", {})
        info = [
            f"DAS: {handling.get('das_ms')} ms",
            f"ARR: {handling.get('arr_ms')} ms",
            f"SDF: {handling.get('sdf')}x",
            "",
            "[TAB] Toggle Settings",
            "[Q] Type Queue (I,J,L...)",
            "[Ctrl+Z/Y] Undo / Redo",
            "[R] Reset Board",
            "[I] Import Screenshot",
            "[L/R-Click] Paint/Hold/Queue",
        ]
        y = 200
        for line in info:
            txt = self.font.render(line, True, (160, 160, 180))
            self.screen.blit(txt, (35, y))
            y += 24

    def _draw_palette(self, input_handler):
        box_rect = pygame.Rect(35, 390, 160, 260)
        pygame.draw.rect(self.screen, (10, 10, 15), box_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, box_rect, 2)

        txt = self.title_font.render("BRUSH", True, (200, 200, 200))
        self.screen.blit(txt, (box_rect.x + 10, box_rect.y + 8))

        selected = input_handler.selected_paint_piece if input_handler else 'G'

        palette_items = ['G', 'I', 'J', 'L', 'O', 'S', 'T', 'Z', None]
        for idx, p_type in enumerate(palette_items):
            col = idx % 2
            row = idx // 2
            bx = box_rect.x + 12 + col * 70
            by = 390 + 38 + row * 40
            rect = pygame.Rect(bx, by, 62, 32)

            is_sel = (p_type == selected)
            bg_col = (40, 50, 70) if is_sel else (20, 22, 30)
            pygame.draw.rect(self.screen, bg_col, rect, border_radius=4)

            border_col = (0, 240, 240) if is_sel else BORDER_COLOR
            pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=4)

            if p_type is None:
                lbl = self.font.render("ERASE", True, (200, 100, 100))
                self.screen.blit(lbl, (bx + (62 - lbl.get_width()) // 2, by + 7))
            else:
                color = COLORS.get(p_type, (150, 150, 150))
                pygame.draw.rect(self.screen, color, (bx + 8, by + 8, 16, 16), border_radius=2)
                lbl = self.font.render(p_type, True, (220, 220, 220))
                self.screen.blit(lbl, (bx + 32, by + 7))

    def _draw_settings_panel(self, config, input_handler):
        in_settings = input_handler.in_settings if input_handler else False
        if not in_settings:
            return

        panel_rect = pygame.Rect(GRID_OFFSET_X + 10, GRID_OFFSET_Y + 10, 280, 580)
        pygame.draw.rect(self.screen, (10, 10, 15), panel_rect, border_radius=8)

        border_col = (0, 200, 240)
        pygame.draw.rect(self.screen, border_col, panel_rect, 2, border_radius=8)

        header_str = "SETTINGS (ACTIVE)"
        txt = self.title_font.render(header_str, True, (0, 240, 240))
        self.screen.blit(txt, (panel_rect.x + 10, panel_rect.y + 10))

        y = panel_rect.y + 42
        sel_idx = input_handler.selected_setting_index if input_handler else -1
        rebinding = input_handler.rebinding if input_handler else False

        for i, (item_key, category, label) in enumerate(SETTINGS_ITEMS):
            is_selected = in_settings and (i == sel_idx)

            if category == "handling":
                val = config.get("handling", {}).get(item_key, 0.0)
                if isinstance(val, bool):
                    val_str = "ON" if val else "OFF"
                else:
                    val_str = f"{val:.1f}ms"
            else: # keybinds
                k_code = config.get("keybinds", {}).get(item_key, 0)
                if is_selected and rebinding:
                    val_str = "<PRESS KEY>"
                else:
                    val_str = pygame.key.name(k_code).upper() if k_code else "NONE"

            item_bg = (40, 50, 70) if is_selected else (20, 22, 30)
            item_rect = pygame.Rect(panel_rect.x + 8, y, 264, 28)
            pygame.draw.rect(self.screen, item_bg, item_rect, border_radius=4)

            label_col = (255, 255, 255) if is_selected else (160, 160, 180)
            val_col = (240, 200, 0) if (is_selected and rebinding) else ((0, 240, 200) if is_selected else (200, 200, 200))

            lbl_txt = self.font.render(label, True, label_col)
            val_txt = self.font.render(val_str, True, val_col)

            self.screen.blit(lbl_txt, (item_rect.x + 6, item_rect.y + 5))
            self.screen.blit(val_txt, (item_rect.right - val_txt.get_width() - 6, item_rect.y + 5))

            y += 32

        if in_settings:
            help_msg = "Up/Down: Select | Left/Right: Adj | Enter: Rebind"
            help_txt = self.font.render(help_msg, True, (120, 140, 160))
            self.screen.blit(help_txt, (panel_rect.x + 5, panel_rect.bottom - 25))
