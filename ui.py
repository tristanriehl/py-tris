import pygame
from engine import COLORS, TETROMINOES, BOARD_WIDTH, VISIBLE_HEIGHT

from input import SETTINGS_ITEMS

CELL_SIZE = 30
GRID_OFFSET_X = 260
GRID_OFFSET_Y = 30
WINDOW_WIDTH = 780
WINDOW_HEIGHT = 730

BACKGROUND_COLOR = (0x66, 0x66, 0x6E)
SURFACE_COLOR = (0x99, 0x99, 0xA1)
SURFACE_ALT_COLOR = (120, 120, 130)
GRID_LINE_COLOR = (140, 140, 150)
BORDER_COLOR = (150, 150, 160)
TEXT_MAIN = (0xF4, 0xF4, 0xF6)
TEXT_MUTED = (210, 210, 220)
ACCENT_COLOR = (0, 180, 255)
ACCENT_WARN = (255, 200, 0)

class Renderer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("TETR.IO Modular Practice Engine")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        self.font = pygame.font.SysFont("Helvetica", 13)
        self.title_font = pygame.font.SysFont("Helvetica", 14, bold=True)
        self.header_font = pygame.font.SysFont("Helvetica", 16, bold=True)

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
        # Board container with modern card styling & subtle drop shadow appearance
        board_rect = pygame.Rect(
            GRID_OFFSET_X, GRID_OFFSET_Y,
            BOARD_WIDTH * CELL_SIZE, VISIBLE_HEIGHT * CELL_SIZE
        )
        # Background fill
        pygame.draw.rect(self.screen, SURFACE_COLOR, board_rect, border_radius=6)
        pygame.draw.rect(self.screen, BORDER_COLOR, board_rect, 2, border_radius=6)

        # Draw grid lines
        for x in range(1, BOARD_WIDTH):
            px = GRID_OFFSET_X + x * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (px, GRID_OFFSET_Y + 2), (px, GRID_OFFSET_Y + VISIBLE_HEIGHT * CELL_SIZE - 2))
        for y in range(1, VISIBLE_HEIGHT):
            py = GRID_OFFSET_Y + y * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (GRID_OFFSET_X + 2, py), (GRID_OFFSET_X + BOARD_WIDTH * CELL_SIZE - 2, py))

        # Render stack
        for r in range(20, 40):
            for c in range(BOARD_WIDTH):
                piece_type = engine.board[r][c]
                if piece_type:
                    color = COLORS.get(piece_type, (150, 150, 150))
                    self._draw_cell(c, r - 20, color)

        # Render active piece & ghost
        if engine.active_piece and not engine.game_over:
            # Ghost piece (increased visibility with a stronger mix towards white/surface color and thicker border)
            ghost_y = engine.get_ghost_y()
            base_col = COLORS[engine.active_piece.type]
            ghost_color = tuple(min(255, int(c + (255 - c) * 0.65)) for c in base_col)
            for bx, by in engine.active_piece.get_blocks(y=ghost_y):
                if by >= 20:
                    self._draw_cell(bx, by - 20, ghost_color, border_only=True, ghost=True)

            # Active piece
            active_color = COLORS[engine.active_piece.type]
            for bx, by in engine.active_piece.get_blocks():
                if by >= 20:
                    self._draw_cell(bx, by - 20, active_color)

    def _draw_cell(self, grid_x, grid_y, color, border_only=False, ghost=False):
        px = GRID_OFFSET_X + grid_x * CELL_SIZE
        py = GRID_OFFSET_Y + grid_y * CELL_SIZE
        rect = pygame.Rect(px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2)

        if border_only:
            border_width = 4 if ghost else 2
            pygame.draw.rect(self.screen, color, rect, border_width, border_radius=4)
        else:
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            # Add soft inner highlight for modern glossy feel
            highlight_rect = pygame.Rect(px + 3, py + 3, CELL_SIZE - 6, 4)
            highlight_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
            pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=2)

    def _draw_hold(self, engine):
        box_rect = pygame.Rect(30, GRID_OFFSET_Y, 200, 100)
        pygame.draw.rect(self.screen, SURFACE_COLOR, box_rect, border_radius=8)
        pygame.draw.rect(self.screen, BORDER_COLOR, box_rect, 1, border_radius=8)

        txt = self.header_font.render("HOLD", True, TEXT_MAIN)
        self.screen.blit(txt, (box_rect.x + 14, box_rect.y + 12))

        if engine.hold_piece:
            color = COLORS[engine.hold_piece] if engine.can_hold else (160, 160, 175)
            blocks = TETROMINOES[engine.hold_piece][0]
            for bx, by in blocks:
                px = box_rect.x + 110 + bx * 18
                py = box_rect.y + 45 + by * 18
                pygame.draw.rect(self.screen, color, (px, py, 16, 16), border_radius=3)

    def _draw_queue(self, engine, input_handler=None):
        box_rect = pygame.Rect(580, GRID_OFFSET_Y, 170, 400)
        pygame.draw.rect(self.screen, SURFACE_COLOR, box_rect, border_radius=8)

        in_queue_input = input_handler.in_queue_input if input_handler else False
        border_col = ACCENT_WARN if in_queue_input else BORDER_COLOR
        pygame.draw.rect(self.screen, border_col, box_rect, 2 if in_queue_input else 1, border_radius=8)

        title_str = "NEXT (TYPING)" if in_queue_input else "NEXT"
        txt = self.header_font.render(title_str, True, ACCENT_WARN if in_queue_input else TEXT_MAIN)
        self.screen.blit(txt, (box_rect.x + 14, box_rect.y + 12))

        # Active Queue Input Text Box Indicator
        if in_queue_input:
            input_box = pygame.Rect(box_rect.x + 12, box_rect.y + 38, 146, 26)
            pygame.draw.rect(self.screen, SURFACE_ALT_COLOR, input_box, border_radius=4)
            pygame.draw.rect(self.screen, ACCENT_WARN, input_box, 1, border_radius=4)
            q_str = "".join(engine.queue[-7:]) + "_"
            q_txt = self.font.render(q_str, True, ACCENT_WARN)
            self.screen.blit(q_txt, (input_box.x + 6, input_box.y + 6))

        start_y = 70 if in_queue_input else 42
        for i in range(min(5, len(engine.queue))):
            piece_type = engine.queue[i]
            color = COLORS[piece_type]
            blocks = TETROMINOES[piece_type][0]
            slot_rect = pygame.Rect(box_rect.x + 12, box_rect.y + start_y + i * 62, 146, 56)
            pygame.draw.rect(self.screen, SURFACE_ALT_COLOR, slot_rect, border_radius=6)
            pygame.draw.rect(self.screen, BORDER_COLOR, slot_rect, 1, border_radius=6)
            for bx, by in blocks:
                px = slot_rect.x + 45 + bx * 15
                py = slot_rect.y + 10 + by * 15
                pygame.draw.rect(self.screen, color, (px, py, 14, 14), border_radius=2)

    def _draw_info_overlay(self, config):
        handling = config.get("handling", {})
        keybinds = config.get("keybinds", {})
        box_rect = pygame.Rect(30, 310, 200, 230)
        pygame.draw.rect(self.screen, SURFACE_COLOR, box_rect, border_radius=8)
        pygame.draw.rect(self.screen, BORDER_COLOR, box_rect, 1, border_radius=8)

        txt = self.header_font.render("CONTROLS & INFO", True, TEXT_MAIN)
        self.screen.blit(txt, (box_rect.x + 14, box_rect.y + 12))

        reset_key = pygame.key.name(keybinds.get("reset", pygame.K_r)).upper()
        import_key = pygame.key.name(keybinds.get("import_screenshot", pygame.K_i)).upper()

        info = [
            f"DAS: {handling.get('das_ms')}ms  |  ARR: {handling.get('arr_ms')}ms",
            f"SDF: {handling.get('sdf')}x",
            "",
            "[TAB] Toggle Settings",
            "[Q] Type Queue",
            "[Ctrl + Z/Y] Undo / Redo",
            f"[{reset_key}] Reset Board",
            f"[{import_key}] Import Screenshot",
            "[Click/Drag] Paint Board",
        ]
        y = box_rect.y + 38
        for line in info:
            line_color = TEXT_MUTED if line.startswith("[") or "ms" in line or "x" in line else TEXT_MAIN
            if line == "":
                y += 6
                continue
            txt = self.font.render(line, True, line_color)
            self.screen.blit(txt, (box_rect.x + 14, y))
            y += 20

    def _draw_palette(self, input_handler):
        box_rect = pygame.Rect(30, 115, 200, 180)
        pygame.draw.rect(self.screen, SURFACE_COLOR, box_rect, border_radius=8)
        pygame.draw.rect(self.screen, BORDER_COLOR, box_rect, 1, border_radius=8)

        txt = self.header_font.render("BRUSH PALETTE", True, TEXT_MAIN)
        self.screen.blit(txt, (box_rect.x + 14, box_rect.y + 12))

        selected = input_handler.selected_paint_piece if input_handler else 'G'

        palette_items = ['G', 'I', 'J', 'L', 'O', 'S', 'T', 'Z', None]
        for idx, p_type in enumerate(palette_items):
            col = idx % 2
            row = idx // 2
            bx = box_rect.x + 12 + col * 90
            by = box_rect.y + 38 + row * 28
            rect = pygame.Rect(bx, by, 86, 24)

            is_sel = (p_type == selected)
            bg_col = (110, 110, 125) if is_sel else SURFACE_ALT_COLOR
            pygame.draw.rect(self.screen, bg_col, rect, border_radius=4)

            border_col = ACCENT_COLOR if is_sel else BORDER_COLOR
            pygame.draw.rect(self.screen, border_col, rect, 1 if not is_sel else 2, border_radius=4)

            if p_type is None:
                lbl = self.font.render("ERASE", True, (255, 120, 120))
                self.screen.blit(lbl, (bx + (86 - lbl.get_width()) // 2, by + 5))
            else:
                color = COLORS.get(p_type, (150, 150, 150))
                pygame.draw.rect(self.screen, color, (bx + 6, by + 5, 14, 14), border_radius=3)
                lbl = self.font.render(p_type, True, TEXT_MAIN)
                self.screen.blit(lbl, (bx + 26, by + 4))

    def _draw_settings_panel(self, config, input_handler):
        in_settings = input_handler.in_settings if input_handler else False
        if not in_settings:
            return

        panel_rect = pygame.Rect(GRID_OFFSET_X + 15, GRID_OFFSET_Y + 15, 290, 575)
        pygame.draw.rect(self.screen, (110, 110, 120), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, panel_rect, 2, border_radius=10)

        header_str = "SETTINGS"
        txt = self.header_font.render(header_str, True, ACCENT_COLOR)
        self.screen.blit(txt, (panel_rect.x + 16, panel_rect.y + 16))

        y = panel_rect.y + 48
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

            item_bg = (110, 110, 125) if is_selected else SURFACE_ALT_COLOR
            item_rect = pygame.Rect(panel_rect.x + 12, y, 266, 26)
            pygame.draw.rect(self.screen, item_bg, item_rect, border_radius=5)

            label_col = TEXT_MAIN if is_selected else TEXT_MUTED
            val_col = ACCENT_WARN if (is_selected and rebinding) else (ACCENT_COLOR if is_selected else TEXT_MAIN)

            lbl_txt = self.font.render(label, True, label_col)
            val_txt = self.font.render(val_str, True, val_col)

            self.screen.blit(lbl_txt, (item_rect.x + 8, item_rect.y + 5))
            self.screen.blit(val_txt, (item_rect.right - val_txt.get_width() - 8, item_rect.y + 5))

            y += 30

        if in_settings:
            help_msg = "Up/Down: Select | Left/Right: Adjust | Enter: Rebind"
            help_txt = self.font.render(help_msg, True, TEXT_MUTED)
            self.screen.blit(help_txt, (panel_rect.x + 14, panel_rect.bottom - 28))
