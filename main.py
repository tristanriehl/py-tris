import json
import pygame
from engine import TetrisEngine
from input import InputHandler
from ui import Renderer
from importer import load_and_parse_screenshot

CONFIG_PATH = "config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config.json: {e}")
        return {}

def main():
    config = load_config()
    
    engine = TetrisEngine(
        lock_delay_ms=config.get("handling", {}).get("lock_delay_ms", 500.0),
        max_lock_resets=config.get("handling", {}).get("max_lock_resets", 15)
    )
    
    input_handler = InputHandler(config)
    renderer = Renderer()

    clock = pygame.time.Clock()
    running = True

    def import_cb():
        load_and_parse_screenshot("test.png", engine)

    while running:
        dt_ms = clock.tick(120)  # Smooth 120 FPS target for Mac displays
        
        running = input_handler.process_input(engine, importer_callback=import_cb)
        engine.update(dt_ms)
        renderer.render(engine, config)

    pygame.quit()

if __name__ == "__main__":
    main()
