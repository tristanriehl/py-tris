import time
import pygame

class InputHandler:
    def __init__(self, config):
        self.update_config(config)

        self.left_pressed = False
        self.right_pressed = False
        self.soft_drop_pressed = False

        self.left_das_timer = 0.0
        self.right_das_timer = 0.0
        self.left_arr_timer = 0.0
        self.right_arr_timer = 0.0
        self.soft_drop_timer = 0.0

        self.last_time = time.perf_counter()

    def update_config(self, config):
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

        # Continuous Input Processing (DAS / ARR / Soft Drop)
        self._handle_das_arr(dt_ms, engine)
        self._handle_soft_drop(dt_ms, engine)

        return True

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
