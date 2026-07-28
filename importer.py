import os
import tempfile
import subprocess
import cv2
import numpy as np
from PIL import Image

COLOR_TARGETS = {
    'I': (0, 240, 240),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
    'O': (240, 240, 0),
    'S': (0, 240, 0),
    'T': (160, 0, 240),
    'Z': (240, 0, 0),
    'G': (128, 128, 128)
}

def load_and_parse_screenshot(image_path, engine):
    """
    Parses a screenshot of a TETR.IO playfield and loads the board state into engine.
    """
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return False

    img = cv2.imread(image_path)
    if img is None:
        return False

    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Simple automatic playfield detection using contour detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    playfield_crop = None
    if contours:
        # Find largest rectangular contour matching 1:2 aspect ratio approximately
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = float(h) / w if w > 0 else 0
            if 1.8 <= aspect_ratio <= 2.2 and w > 100:
                playfield_crop = img_rgb[y:y+h, x:x+w]
                break

    if playfield_crop is None:
        # Fallback: assume whole image is board area
        playfield_crop = img_rgb

    height, width, _ = playfield_crop.shape
    cell_h = height / 20.0
    cell_w = width / 10.0

    # Reset stack
    new_board = [[None for _ in range(10)] for _ in range(40)]

    for r in range(20):
        for c in range(10):
            cy_start, cy_end = int(r * cell_h), int((r + 1) * cell_h)
            cx_start, cx_end = int(c * cell_w), int((c + 1) * cell_w)

            # Sample central area of cell to avoid border artifacts
            pad_h = int((cy_end - cy_start) * 0.25)
            pad_w = int((cx_end - cx_start) * 0.25)
            sample = playfield_crop[cy_start+pad_h:cy_end-pad_h, cx_start+pad_w:cx_end-pad_w]

            if sample.size == 0:
                continue

            avg_color = np.mean(sample, axis=(0, 1))

            # Classify color against targets
            if np.mean(avg_color) > 15:  # Non-black block
                closest_piece = 'G'
                min_dist = float('inf')
                for piece, color in COLOR_TARGETS.items():
                    dist = np.linalg.norm(avg_color - np.array(color))
                    if dist < min_dist:
                        min_dist = dist
                        closest_piece = piece

                # Map 0..19 visible grid to 20..39 board coordinates
                new_board[20 + r][c] = closest_piece

    engine.board = new_board
    engine.spawn_piece()
    print("Successfully imported screenshot board state!")
    return True

def capture_and_parse_screenshot(engine):
    """
    Triggers OS screenshot tool to take a selection, then loads board state.
    """
    temp_path = os.path.join(tempfile.gettempdir(), "tetris_screenshot.png")
    if os.path.exists(temp_path):
        os.remove(temp_path)

    try:
        subprocess.run(["screencapture", "-i", temp_path], check=True)
    except Exception as e:
        print(f"Screenshot capture cancelled or failed: {e}")
        return False

    if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
        print("No screenshot captured.")
        return False

    return load_and_parse_screenshot(temp_path, engine)
