import time
import pygame

SETTINGS_ITEMS = [
    ("das_ms", "handling", "DAS (ms)"),
    ("arr_ms", "handling", "ARR (ms)"),
    ("infinite_hold", "handling", "Infinite Hold"),
    ("move_left", "keybinds", "Move Left"),
    ("move_right", "keybinds", "Move Right"),
    ("soft_drop", "keybinds", "Soft Drop"),
    ("hard_drop", "keybinds", "Hard Drop"),
    ("rotate_cw", "keybinds", "Rotate CW"),
    ("rotate_ccw", "keybinds", "Rotate CCW"),
    ("rotate_180", "keybinds", "Rotate 180"),
    ("hold", "keybinds", "Hold"),
    ("reset", "keybinds", "Reset"),
    ("import_screenshot", "keybinds", "Import Board")
]

class InputHandler:
    def __init__(self, config, save_config_cb=None):
        self.config = config
        self.save_config_cb = save_config_cb
        self.update_config(config)

        self.left_pressed = False
        self.right_pressed = False
        self.soft_drop_pressed = False

        self.left_das_timer = 0.0
        self.right_das_timer = 0.0
        self.left_arr_timer = 0.0
        self.right_arr_timer = 0.0
        self.soft_drop_timer = 0.0

        self.in_settings = False
        self.selected_setting_index = 0
        self.rebinding = False

        self.in_queue_input = False
        self.selected_paint_piece = 'G'
        self.mouse_left_down = False
        self.mouse_right_down = False

        self.last_time = time.perf_counter()

    def update_config(self, config):
        self.config = config
        handling = config.get("handling", {})
        self.das_ms = handling.get("das_ms", 133.0)
        self.arr_ms = handling.get("arr_ms", 0.0)
        self.sdf = handling.get("sdf", 40.0)
        self.dcd_ms = handling.get("dcd_ms", 0.0)
        self.infinite_hold = handling.get("infinite_hold", True)
        self.keybinds = config.get("keybinds", {})

    def process_input(self, engine, importer_callback=None):
        engine.infinite_hold = self.infinite_hold
        now = time.perf_counter()
        dt_ms = (now - self.last_time) * 1000.0
        self.last_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                key = event.key

                mods = pygame.key.get_mods()
                is_cmd_or_ctrl = bool(mods & (pygame.KMOD_CTRL | pygame.KMOD_META))
                is_shift = bool(mods & pygame.KMOD_SHIFT)

                # Undo / Redo handling
                if is_cmd_or_ctrl and not self.rebinding and not self.in_settings:
                    if key == pygame.K_z:
                        if is_shift:
                            engine.redo()
                        else:
                            engine.undo()
                        continue
                    elif key == pygame.K_y:
                        engine.redo()
                        continue

                # Rebinding mode takes precedence
                if self.rebinding:
                    key_name, category, _ = SETTINGS_ITEMS[self.selected_setting_index]
                    if category == "keybinds":
                        self.config["keybinds"][key_name] = key
                        self.update_config(self.config)
                        if self.save_config_cb:
                            self.save_config_cb(self.config)
                    self.rebinding = False
                    continue

                # Toggle queue typing mode with Q or ESC/Enter while in queue input
                if self.in_queue_input:
                    if key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        self.in_queue_input = False
                        continue
                    elif key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        if engine.queue:
                            engine.queue.pop()
                        continue
                    elif key == pygame.K_c and (pygame.key.get_mods() & (pygame.KMOD_CTRL | pygame.KMOD_META)):
                        engine.queue.clear()
                        continue
                    else:
                        char = event.unicode.upper()
                        if char in ['I', 'J', 'L', 'O', 'S', 'T', 'Z']:
                            engine.queue.append(char)
                        continue

                if key == pygame.K_q and not self.in_settings:
                    self.in_queue_input = True
                    continue

                # Toggle settings mode with TAB or ESC
                if key in (pygame.K_TAB, pygame.K_ESCAPE):
                    self.in_settings = not self.in_settings
                    self.left_pressed = False
                    self.right_pressed = False
                    self.soft_drop_pressed = False
                    continue

                if self.in_settings:
                    self._handle_settings_keydown(key)
                    continue

                # Shift + Piece Key for quick queue entry (only consume event if shift is held AND it's a piece key)
                if is_shift and event.unicode.upper() in ['I', 'J', 'L', 'O', 'S', 'T', 'Z']:
                    engine.queue.append(event.unicode.upper())
                    continue

                # In-game key handling
                if key == self.keybinds.get("move_left"):
                    self.left_pressed = True
                    self.left_das_timer = 0.0
                    self.left_arr_timer = 0.0
                    engine.move_left()
                    self.right_pressed = False

                elif key == self.keybinds.get("move_right"):
                    self.right_pressed = True
                    self.right_das_timer = 0.0
                    self.right_arr_timer = 0.0
                    engine.move_right()
                    self.left_pressed = False

                elif key == self.keybinds.get("soft_drop"):
                    self.soft_drop_pressed = True
                    self.soft_drop_timer = 0.0

                elif key == self.keybinds.get("hard_drop"):
                    engine.hard_drop()

                elif key == self.keybinds.get("rotate_cw"):
                    engine.rotate('CW')

                elif key == self.keybinds.get("rotate_ccw"):
                    engine.rotate('CCW')

                elif key == self.keybinds.get("rotate_180"):
                    engine.rotate('180')

                elif key == self.keybinds.get("hold"):
                    engine.hold()

                elif key == self.keybinds.get("reset"):
                    engine.reset_board()

                elif key == self.keybinds.get("import_screenshot"):
                    if importer_callback:
                        importer_callback()

            elif event.type == pygame.KEYUP:
                key = event.key
                if key == self.keybinds.get("move_left"):
                    self.left_pressed = False
                elif key == self.keybinds.get("move_right"):
                    self.right_pressed = False
                elif key == self.keybinds.get("soft_drop"):
                    self.soft_drop_pressed = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 3):
                    if event.button == 1:
                        self.mouse_left_down = True
                        self._handle_mouse_click(event.pos, engine, is_left=True)
                    elif event.button == 3:
                        self.mouse_right_down = True
                        self._handle_mouse_click(event.pos, engine, is_left=False)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_left_down = False
                elif event.button == 3:
                    self.mouse_right_down = False

            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_left_down:
                    self._handle_board_drag(event.pos, engine, paint=True)
                elif self.mouse_right_down:
                    self._handle_board_drag(event.pos, engine, paint=False)

        if not self.in_settings:
            # Continuous Input Processing (DAS / ARR / Soft Drop)
            self._handle_das_arr(dt_ms, engine)
            self._handle_soft_drop(dt_ms, engine)

        return True

    def _handle_mouse_click(self, pos, engine, is_left):
        if self.in_settings:
            return

        mx, my = pos

        # Check Palette click
        palette_items = ['G', 'I', 'J', 'L', 'O', 'S', 'T', 'Z', None]
        if 35 <= mx < 195 and 390 <= my < 650:
            for idx, p_type in enumerate(palette_items):
                col = idx % 2
                row = idx // 2
                bx = 35 + 12 + col * 70
                by = 390 + 38 + row * 40
                if bx <= mx < bx + 62 and by <= my < by + 32:
                    self.selected_paint_piece = p_type
                    return

        # Check Hold Box click
        if 50 <= mx < 180 and 50 <= my < 170:
            engine.save_state()
            tetro_types = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
            if is_left and self.selected_paint_piece in tetro_types:
                engine.hold_piece = self.selected_paint_piece
            elif is_left and self.selected_paint_piece is None:
                engine.hold_piece = None
            else:
                curr = engine.hold_piece
                curr_idx = tetro_types.index(curr) if curr in tetro_types else -1
                step = 1 if is_left else -1
                next_type = tetro_types[(curr_idx + step) % len(tetro_types)]
                engine.hold_piece = next_type
            return

        # Check Queue click
        if 540 <= mx < 670 and 50 <= my < 470:
            self.in_queue_input = True
            for i in range(min(5, len(engine.queue))):
                qy = 50 + 45 + i * 70
                if qy <= my < qy + 65:
                    engine.save_state()
                    tetro_types = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
                    if is_left and self.selected_paint_piece in tetro_types:
                        engine.queue[i] = self.selected_paint_piece
                    else:
                        curr = engine.queue[i]
                        curr_idx = tetro_types.index(curr) if curr in tetro_types else 0
                        step = 1 if is_left else -1
                        next_type = tetro_types[(curr_idx + step) % len(tetro_types)]
                        engine.queue[i] = next_type
                    return

        # Check Board click
        self._handle_board_drag(pos, engine, paint=is_left)

    def _handle_board_drag(self, pos, engine, paint):
        if self.in_settings:
            return

        mx, my = pos
        grid_x = (mx - 220) // 30
        grid_y = (my - 50) // 30
        if 0 <= grid_x < 10 and 0 <= grid_y < 20:
            board_r = 20 + grid_y
            new_val = self.selected_paint_piece if paint else None
            if engine.board[board_r][grid_x] != new_val:
                engine.save_state()
                engine.board[board_r][grid_x] = new_val

    def _handle_settings_keydown(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self.selected_setting_index = (self.selected_setting_index - 1) % len(SETTINGS_ITEMS)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.selected_setting_index = (self.selected_setting_index + 1) % len(SETTINGS_ITEMS)
        else:
            item_key, category, _ = SETTINGS_ITEMS[self.selected_setting_index]

            if category == "handling":
                if item_key == "infinite_hold":
                    if key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d, pygame.K_RETURN, pygame.K_SPACE):
                        curr = self.config["handling"].get("infinite_hold", True)
                        self.config["handling"]["infinite_hold"] = not curr
                        self.update_config(self.config)
                        if self.save_config_cb:
                            self.save_config_cb(self.config)
                else:
                    val = float(self.config["handling"].get(item_key, 0.0))
                    step = 1.0 if item_key == "arr_ms" else 5.0

                    if key in (pygame.K_LEFT, pygame.K_a, pygame.K_MINUS, pygame.K_KP_MINUS):
                        val = max(0.0, val - step)
                        self.config["handling"][item_key] = val
                        self.update_config(self.config)
                        if self.save_config_cb:
                            self.save_config_cb(self.config)

                    elif key in (pygame.K_RIGHT, pygame.K_d, pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                        val += step
                        self.config["handling"][item_key] = val
                        self.update_config(self.config)
                        if self.save_config_cb:
                            self.save_config_cb(self.config)

            elif category == "keybinds":
                if key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.rebinding = True

    def _handle_das_arr(self, dt_ms, engine):
        if self.left_pressed:
            self.left_das_timer += dt_ms
            if self.left_das_timer >= self.das_ms:
                if self.arr_ms == 0:
                    while engine.move_left():
                        pass
                else:
                    self.left_arr_timer += dt_ms
                    while self.left_arr_timer >= self.arr_ms:
                        if not engine.move_left():
                            break
                        self.left_arr_timer -= self.arr_ms

        if self.right_pressed:
            self.right_das_timer += dt_ms
            if self.right_das_timer >= self.das_ms:
                if self.arr_ms == 0:
                    while engine.move_right():
                        pass
                else:
                    self.right_arr_timer += dt_ms
                    while self.right_arr_timer >= self.arr_ms:
                        if not engine.move_right():
                            break
                        self.right_arr_timer -= self.arr_ms

    def _handle_soft_drop(self, dt_ms, engine):
        if self.soft_drop_pressed:
            if self.sdf >= 40.0:  # Instant soft drop
                while engine.soft_drop():
                    pass
            else:
                drop_interval = 50.0 / self.sdf
                self.soft_drop_timer += dt_ms
                while self.soft_drop_timer >= drop_interval:
                    if not engine.soft_drop():
                        break
                    self.soft_drop_timer -= drop_interval
