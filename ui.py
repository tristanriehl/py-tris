import pygame
from engine import COLORS, TETROMINOES, BOARD_WIDTH, VISIBLE_HEIGHT

from input import SETTINGS_ITEMS

BASE_CELL_SIZE = 30
BASE_GRID_OFFSET_X = 260
BASE_GRID_OFFSET_Y = 30
BASE_WINDOW_WIDTH = 780
BASE_WINDOW_HEIGHT = 730

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
        self.screen = pygame.display.set_mode((BASE_WINDOW_WIDTH, BASE_WINDOW_HEIGHT), pygame.RESIZABLE)
        self.font = pygame.font.SysFont("Helvetica", 13)
        self.title_font = pygame.font.SysFont("Helvetica", 14, bold=True)
        self.header_font = pygame.font.SysFont("Helvetica", 16, bold=True)

    def render(self, engine, config, input_handler=None):
        win_w, win_h = self.screen.get_size()
        
        # Calculate adaptive scale factor based on both width and height to prevent any clipping/hiding
        scale_w = win_w / float(BASE_WINDOW_WIDTH)
        scale_h = win_h / float(BASE_WINDOW_HEIGHT)
        scale = min(scale_w, scale_h)
        
        # Center the content horizontally in the window
        content_w = BASE_WINDOW_WIDTH * scale
        offset_x = max(0, (win_w - content_w) / 2.0)

        self.screen.fill(BACKGROUND_COLOR)

        self._draw_board(engine, scale, offset_x)
        self._draw_hold(engine, scale, offset_x)
        self._draw_queue(engine, input_handler, scale, offset_x)
        self._draw_info_overlay(config, scale, offset_x)
        self._draw_palette(input_handler, scale, offset_x)
        self._draw_settings_panel(config, input_handler, scale, offset_x)

        pygame.display.flip()

    def _draw_board(self, engine, scale, offset_x):
        cell_size = int(BASE_CELL_SIZE * scale)
        grid_offset_x = int(offset_x + BASE_GRID_OFFSET_X * scale)
        grid_offset_y = int(BASE_GRID_OFFSET_Y * scale)

        board_rect = pygame.Rect(
            grid_offset_x, grid_offset_y,
            BOARD_WIDTH * cell_size, VISIBLE_HEIGHT * cell_size
        )
        pygame.draw.rect(self.screen, SURFACE_COLOR, board_rect, border_radius=int(6 * scale))
        pygame.draw.rect(self.screen, BORDER_COLOR, board_rect, max(1, int(2 * scale)), border_radius=int(6 * scale))

        # Draw grid lines
        for x in range(1, BOARD_WIDTH):
            px = grid_offset_x + x * cell_size
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (px, grid_offset_y + int(2 * scale)), (px, grid_offset_y + VISIBLE_HEIGHT * cell_size - int(2 * scale)), max(1, int(scale)))
        for y in range(1, VISIBLE_HEIGHT):
            py = grid_offset_y + y * cell_size
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (grid_offset_x + int(2 * scale), py), (grid_offset_x + BOARD_WIDTH * cell_size - int(2 * scale), py), max(1, int(scale)))

        # Render stack
        for r in range(20, 40):
            for c in range(BOARD_WIDTH):
                piece_type = engine.board[r][c]
                if piece_type:
                    color = COLORS.get(piece_type, (150, 150, 150))
                    self._draw_cell(c, r - 20, color, scale, grid_offset_x, grid_offset_y, cell_size)

        # Render active piece & ghost
        if engine.active_piece and not engine.game_over:
            ghost_y = engine.get_ghost_y()
            base_col = COLORS[engine.active_piece.type]
            for bx, by in engine.active_piece.get_blocks(y=ghost_y):
                if by >= 20:
                    self._draw_cell(bx, by - 20, base_col, scale, grid_offset_x, grid_offset_y, cell_size, ghost=True)

            active_color = COLORS[engine.active_piece.type]
            for bx, by in engine.active_piece.get_blocks():
                if by >= 20:
                    self._draw_cell(bx, by - 20, active_color, scale, grid_offset_x, grid_offset_y, cell_size)

    def _draw_cell(self, grid_x, grid_y, color, scale, grid_offset_x, grid_offset_y, cell_size, ghost=False):
        px = grid_offset_x + grid_x * cell_size
        py = grid_offset_y + grid_y * cell_size

        if ghost:
            surf = pygame.Surface((cell_size - max(1, int(2 * scale)), cell_size - max(1, int(2 * scale))), pygame.SRCALPHA)
            ghost_color = (color[0], color[1], color[2], 90)
            pygame.draw.rect(surf, ghost_color, surf.get_rect(), border_radius=int(4 * scale))
            self.screen.blit(surf, (px + max(1, int(scale)), py + max(1, int(scale))))
        else:
            rect = pygame.Rect(px + max(1, int(scale)), py + max(1, int(scale)), cell_size - max(1, int(2 * scale)), cell_size - max(1, int(2 * scale)))
            pygame.draw.rect(self.screen, color, rect, border_radius=int(4 * scale))
            
            highlight_rect = pygame.Rect(px + max(2, int(3 * scale)), py + max(2, int(3 * scale)), cell_size - max(4, int(6 * scale)), max(2, int(4 * scale)))
            highlight_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
            pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=int(2 * scale))

    def _draw_hold(self, engine, scale, offset_x):
        bx_x = offset_x + 30 * scale
        bx_y = BASE_GRID_OFFSET_Y * scale
        box_rect = pygame.Rect(bx_x, bx_y, 200 * scale, 100 * scale)
        pygame.draw.rect(self.screen, SURFACE_COLOR, box_rect, border_radius=int(8 * scale))
        pygame.draw.rect(self.screen, BORDER_COLOR, box_rect, max(1, int(scale)), border_radius=int(8 * scale))

        txt = self.header_font.render("HOLD", True, TEXT_MAIN)
        if scale != 1.0:
            txt = pygame.transform.smoothscale(txt, (int(txt.get_width() * scale), int(txt.get_height() * scale)))
        self.screen.blit(txt, (box_rect.x + 14 * scale, box_rect.y + 12 * scale))

        if engine.hold_piece:
            color = COLORS[engine.hold_piece] if engine.can_hold else (160, 160, 175)
            blocks = TETROMINOES[engine.hold_piece][0]
            for bx, by in blocks:
                px = box_rect.x + 110 * scale + bx * 18 * scale
                py = box_rect.y + 45 * scale + by * 18 * scale
                pygame.draw.rect(self.screen, color, (px, py, 16 * scale, 16 * scale), border_radius=int(3 * scale))

    def _draw_queue(self, engine, input_handler, scale, offset_x):
        bx_x = offset_x + 580 * scale
        bx_y = BASE_GRID_OFFSET_Y * scale
        box_rect = pygame.Rect(bx_x, bx_y, 170 * scale, 400 * scale)
        pygame.draw.rect(self.screen, SURFACE_COLOR, box_rect, border_radius=int(8 * scale))

        in_queue_input = input_handler.in_queue_input if input_handler else False
        border_col = ACCENT_WARN if in_queue_input else BORDER_COLOR
        pygame.draw.rect(self.screen, border_col, box_rect, int((2 if in_queue_input else 1) * scale), border_radius=int(8 * scale))

        title_str = "NEXT (TYPING)" if in_queue_input else "NEXT"
        txt = self.header_font.render(title_str, True, ACCENT_WARN if in_queue_input else TEXT_MAIN)
        if scale != 1.0:
            txt = pygame.transform.smoothscale(txt, (int(txt.get_width() * scale), int(txt.get_height() * scale)))
        self.screen.blit(txt, (box_rect.x + 14 * scale, box_rect.y + 12 * scale))

        if in_queue_input:
            input_box = pygame.Rect(box_rect.x + 12 * scale, box_rect.y + 38 * scale, 146 * scale, 26 * scale)
            pygame.draw.rect(self.screen, SURFACE_ALT_COLOR, input_box, border_radius=int(4 * scale))
            pygame.draw.rect(self.screen, ACCENT_WARN, input_box, max(1, int(scale)), border_radius=int(4 * scale))
            q_str = "".join(engine.queue[-7:]) + "_"
            q_txt = self.font.render(q_str, True, ACCENT_WARN)
            if scale != 1.0:
                q_txt = pygame.transform.smoothscale(q_txt, (int(q_txt.get_width() * scale), int(q_txt.get_height() * scale)))
            self.screen.blit(q_txt, (input_box.x + 6 * scale, input_box.y + 6 * scale))

        start_y = 70 if in_queue_input else 42
        for i in range(min(5, len(engine.queue))):
            piece_type = engine.queue[i]
            color = COLORS[piece_type]
            blocks = TETROMINOES[piece_type][0]
            slot_rect = pygame.Rect(box_rect.x + 12 * scale, box_rect.y + (start_y + i * 62) * scale, 146 * scale, 56 * scale)
            pygame.draw.rect(self.screen, SURFACE_ALT_COLOR, slot_rect, border_radius=int(6 * scale))
            pygame.draw.rect(self.screen, BORDER_COLOR, slot_rect, max(1, int(scale)), border_radius=int(6 * scale))
            for bx, by in blocks:
                px = slot_rect.x + 45 * scale + bx * 15 * scale
                py = slot_rect.y + 10 * scale + by * 15 * scale
                pygame.draw.rect(self.screen, color, (px, py, 14 * scale, 14 * scale), border_radius=int(2 * scale))

    def _draw_info_overlay(self, config, scale, offset_x):
        handling = config.get("handling", {})
        keybinds = config.get("keybinds", {})
        bx_x = offset_x + 30 * scale
        bx_y = 310 * scale
        box_rect = pygame.Rect(bx_x, bx_y, 200 * scale, 230 * scale)
        pygame.draw.rect(self.screen, SURFACE_COLOR, box_rect, border_radius=int(8 * scale))
        pygame.draw.rect(self.screen, BORDER_COLOR, box_rect, max(1, int(scale)), border_radius=int(8 * scale))

        txt = self.header_font.render("CONTROLS & INFO", True, TEXT_MAIN)
        if scale != 1.0:
            txt = pygame.transform.smoothscale(txt, (int(txt.get_width() * scale), int(txt.get_height() * scale)))
        self.screen.blit(txt, (box_rect.x + 14 * scale, box_rect.y + 12 * scale))

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
        y = box_rect.y + 38 * scale
        for line in info:
            line_color = TEXT_MUTED if line.startswith("[") or "ms" in line or "x" in line else TEXT_MAIN
            if line == "":
                y += 6 * scale
                continue
            txt = self.font.render(line, True, line_color)
            if scale != 1.0:
                txt = pygame.transform.smoothscale(txt, (int(txt.get_width() * scale), int(txt.get_height() * scale)))
            self.screen.blit(txt, (box_rect.x + 14 * scale, y))
            y += 20 * scale

    def _draw_palette(self, input_handler, scale, offset_x):
        bx_x = offset_x + 30 * scale
        bx_y = 115 * scale
        box_rect = pygame.Rect(bx_x, bx_y, 200 * scale, 180 * scale)
        pygame.draw.rect(self.screen, SURFACE_COLOR, box_rect, border_radius=int(8 * scale))
        pygame.draw.rect(self.screen, BORDER_COLOR, box_rect, max(1, int(scale)), border_radius=int(8 * scale))

        txt = self.header_font.render("BRUSH PALETTE", True, TEXT_MAIN)
        if scale != 1.0:
            txt = pygame.transform.smoothscale(txt, (int(txt.get_width() * scale), int(txt.get_height() * scale)))
        self.screen.blit(txt, (box_rect.x + 14 * scale, box_rect.y + 12 * scale))

        selected = input_handler.selected_paint_piece if input_handler else 'G'

        palette_items = ['G', 'I', 'J', 'L', 'O', 'S', 'T', 'Z', None]
        for idx, p_type in enumerate(palette_items):
            col = idx % 2
            row = idx // 2
            bx = box_rect.x + (12 + col * 90) * scale
            by = box_rect.y + (38 + row * 28) * scale
            rect = pygame.Rect(bx, by, 86 * scale, 24 * scale)

            is_sel = (p_type == selected)
            bg_col = (110, 110, 125) if is_sel else SURFACE_ALT_COLOR
            pygame.draw.rect(self.screen, bg_col, rect, border_radius=int(4 * scale))

            border_col = ACCENT_COLOR if is_sel else BORDER_COLOR
            pygame.draw.rect(self.screen, border_col, rect, int((1 if not is_sel else 2) * scale), border_radius=int(4 * scale))

            if p_type is None:
                lbl = self.font.render("ERASE", True, (255, 120, 120))
                if scale != 1.0:
                    lbl = pygame.transform.smoothscale(lbl, (int(lbl.get_width() * scale), int(lbl.get_height() * scale)))
                self.screen.blit(lbl, (bx + (86 * scale - lbl.get_width()) // 2, by + 5 * scale))
            else:
                color = COLORS.get(p_type, (150, 150, 150))
                pygame.draw.rect(self.screen, color, (bx + 6 * scale, by + 5 * scale, 14 * scale, 14 * scale), border_radius=int(3 * scale))
                lbl = self.font.render(p_type, True, TEXT_MAIN)
                if scale != 1.0:
                    lbl = pygame.transform.smoothscale(lbl, (int(lbl.get_width() * scale), int(lbl.get_height() * scale)))
                self.screen.blit(lbl, (bx + 26 * scale, by + 4 * scale))

    def _draw_settings_panel(self, config, input_handler, scale, offset_x):
        in_settings = input_handler.in_settings if input_handler else False
        if not in_settings:
            return

        panel_rect = pygame.Rect(offset_x + (BASE_GRID_OFFSET_X + 15) * scale, (BASE_GRID_OFFSET_Y + 15) * scale, 290 * scale, 575 * scale)
        pygame.draw.rect(self.screen, (110, 110, 120), panel_rect, border_radius=int(10 * scale))
        pygame.draw.rect(self.screen, ACCENT_COLOR, panel_rect, max(1, int(2 * scale)), border_radius=int(10 * scale))

        header_str = "SETTINGS"
        txt = self.header_font.render(header_str, True, ACCENT_COLOR)
        if scale != 1.0:
            txt = pygame.transform.smoothscale(txt, (int(txt.get_width() * scale), int(txt.get_height() * scale)))
        self.screen.blit(txt, (panel_rect.x + 16 * scale, panel_rect.y + 16 * scale))

        y = panel_rect.y + 48 * scale
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
            item_rect = pygame.Rect(panel_rect.x + 12 * scale, y, 266 * scale, 26 * scale)
            pygame.draw.rect(self.screen, item_bg, item_rect, border_radius=int(5 * scale))

            label_col = TEXT_MAIN if is_selected else TEXT_MUTED
            val_col = ACCENT_WARN if (is_selected and rebinding) else (ACCENT_COLOR if is_selected else TEXT_MAIN)

            lbl_txt = self.font.render(label, True, label_col)
            val_txt = self.font.render(val_str, True, val_col)
            if scale != 1.0:
                lbl_txt = pygame.transform.smoothscale(lbl_txt, (int(lbl_txt.get_width() * scale), int(lbl_txt.get_height() * scale)))
                val_txt = pygame.transform.smoothscale(val_txt, (int(val_txt.get_width() * scale), int(val_txt.get_height() * scale)))

            self.screen.blit(lbl_txt, (item_rect.x + 8 * scale, item_rect.y + 5 * scale))
            self.screen.blit(val_txt, (item_rect.right - val_txt.get_width() - 8 * scale, item_rect.y + 5 * scale))

            y += 30 * scale

        if in_settings:
            help_msg = "Up/Down: Select | Left/Right: Adjust | Enter: Rebind"
            help_txt = self.font.render(help_msg, True, TEXT_MUTED)
            if scale != 1.0:
                help_txt = pygame.transform.smoothscale(help_txt, (int(help_txt.get_width() * scale), int(help_txt.get_height() * scale)))
            self.screen.blit(help_txt, (panel_rect.x + 14 * scale, panel_rect.bottom - 28 * scale))
