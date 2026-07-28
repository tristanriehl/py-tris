import os
import time
import tempfile
import subprocess
import cv2
import numpy as np

def classify_cell_hsv(sample_bgr):
    """
    Classifies a cell block sample based on HSV values.
    Returns piece key ('I', 'J', 'L', 'O', 'S', 'T', 'Z', 'G') or None.
    """
    if sample_bgr.size == 0:
        return None

    hsv = cv2.cvtColor(sample_bgr, cv2.COLOR_BGR2HSV)
    avg_hsv = np.mean(hsv, axis=(0, 1))
    h, s, v = avg_hsv[0], avg_hsv[1], avg_hsv[2]

    # Dark / Black empty space (including interior of ghost pieces)
    if v < 40:
        return None

    # Low saturation grey garbage blocks
    if s < 45:
        return 'G'

    # Hue classification (OpenCV H is 0-180)
    if h < 10 or h >= 170:
        return 'Z'  # Red
    elif 10 <= h < 23:
        return 'L'  # Orange
    elif 23 <= h < 38:
        return 'O'  # Yellow
    elif 38 <= h < 80:
        return 'S'  # Lime Green
    elif 80 <= h < 102:
        return 'I'  # Cyan
    elif 102 <= h < 130:
        return 'J'  # Blue
    elif 130 <= h < 170:
        return 'T'  # Purple

    return 'G'

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

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    playfield_crop = None
    if contours:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = float(h) / w if w > 0 else 0
            if 1.7 <= aspect_ratio <= 2.3 and w > 80:
                playfield_crop = img[y:y+h, x:x+w]
                break

    if playfield_crop is None:
        playfield_crop = img

    height, width, _ = playfield_crop.shape
    cell_h = height / 20.0
    cell_w = width / 10.0

    new_board = [[None for _ in range(10)] for _ in range(40)]

    for r in range(20):
        for c in range(10):
            cy_start, cy_end = int(r * cell_h), int((r + 1) * cell_h)
            cx_start, cx_end = int(c * cell_w), int((c + 1) * cell_w)

            # Sample inner 40% region to completely avoid borders and ghost outlines
            pad_h = int((cy_end - cy_start) * 0.3)
            pad_w = int((cx_end - cx_start) * 0.3)
            sample = playfield_crop[cy_start+pad_h:cy_end-pad_h, cx_start+pad_w:cx_end-pad_w]

            piece = classify_cell_hsv(sample)
            if piece:
                new_board[20 + r][c] = piece

    engine.board = new_board
    engine.spawn_piece()
    print("Successfully imported screenshot board state!")
    return True

def capture_and_parse_screenshot(engine):
    """
    Hides the window and triggers OS screenshot tool to select playfield.
    """
    import pygame
    pygame.display.iconify()
    pygame.event.pump()
    time.sleep(0.35)

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
