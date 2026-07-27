import time
import pygame

SETTINGS_ITEMS = [
    ("das_ms", "handling", "DAS (ms)"),
    ("arr_ms", "handling", "ARR (ms)"),
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

        self.last_time = time.perf_counter()

    def update_config(self, config):
        self.config = config
        handling = config.get("handling", {})
        self.das_ms = handling.get("das_ms", 133.0)
        self.arr_ms = handling.get("arr_ms", 0.0)
        self.sdf = handling.get("sdf", 40.0)
        self.dcd_ms = handling.get("dcd_ms", 0.0)
        self.keybinds = config.get("keybinds", {})

    def process_input(self, engine, importer_callback=None):
        now = time.perf_counter()
        dt_ms = (now - self.last_time) * 1000.0
        self.last_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                key = event.key

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

        if not self.in_settings:
            # Continuous Input Processing (DAS / ARR / Soft Drop)
            self._handle_das_arr(dt_ms, engine)
            self._handle_soft_drop(dt_ms, engine)

        return True

    def _handle_settings_keydown(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self.selected_setting_index = (self.selected_setting_index - 1) % len(SETTINGS_ITEMS)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.selected_setting_index = (self.selected_setting_index + 1) % len(SETTINGS_ITEMS)
        else:
            item_key, category, _ = SETTINGS_ITEMS[self.selected_setting_index]

            if category == "handling":
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
