use crate::types::{BoardMatrix, Mino, BOARD_HEIGHT, BOARD_WIDTH, VISIBLE_HEIGHT};

#[derive(Debug, Clone, Copy)]
pub struct RgbColor {
    pub r: u8,
    pub g: u8,
    pub b: u8,
}

#[derive(Debug, Clone, Copy)]
pub struct LabColor {
    pub l: f32,
    pub a: f32,
    pub b: f32,
}

// Convert sRGB to CIELAB space for perceptual color matching
pub fn rgb_to_lab(rgb: RgbColor) -> LabColor {
    let mut r = rgb.r as f32 / 255.0;
    let mut g = rgb.g as f32 / 255.0;
    let mut b = rgb.b as f32 / 255.0;

    r = if r > 0.04045 { ((r + 0.055) / 1.055).powf(2.4) } else { r / 12.92 };
    g = if g > 0.04045 { ((g + 0.055) / 1.055).powf(2.4) } else { g / 12.92 };
    b = if b > 0.04045 { ((b + 0.055) / 1.055).powf(2.4) } else { b / 12.92 };

    let x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047;
    let y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.00000;
    let z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883;

    let f = |t: f32| -> f32 {
        if t > 0.008856 { t.powf(1.0 / 3.0) } else { (7.787 * t) + (16.0 / 116.0) }
    };

    let fx = f(x);
    let fy = f(y);
    let fz = f(z);

    LabColor {
        l: (116.0 * fy) - 16.0,
        a: 500.0 * (fx - fy),
        b: 200.0 * (fy - fz),
    }
}

// Euclidean CIE76 color distance formula
pub fn color_distance(c1: LabColor, c2: LabColor) -> f32 {
    ((c1.l - c2.l).powi(2) + (c1.a - c2.a).powi(2) + (c1.b - c2.b).powi(2)).sqrt()
}

// Standard TETR.IO Mino Reference Colors
static MINO_PALETTE: [(Mino, RgbColor); 8] = [
    (Mino::Empty, RgbColor { r: 15, g: 15, b: 20 }),      // Dark background
    (Mino::I, RgbColor { r: 50, g: 220, b: 220 }),        // Cyan
    (Mino::J, RgbColor { r: 50, g: 80, b: 220 }),         // Blue
    (Mino::L, RgbColor { r: 230, g: 130, b: 40 }),        // Orange
    (Mino::O, RgbColor { r: 230, g: 200, b: 50 }),        // Yellow
    (Mino::S, RgbColor { r: 60, g: 210, b: 70 }),         // Green
    (Mino::T, RgbColor { r: 170, g: 50, b: 210 }),        // Purple
    (Mino::Z, RgbColor { r: 220, g: 50, b: 60 }),         // Red
];

/// Classify a sampled RGB cell color into the matching Mino enum
pub fn classify_color(sampled: RgbColor) -> Mino {
    let target_lab = rgb_to_lab(sampled);
    let mut min_dist = f32::MAX;
    let mut best_mino = Mino::Empty;

    for &(mino, palette_rgb) in &MINO_PALETTE {
        let palette_lab = rgb_to_lab(palette_rgb);
        let dist = color_distance(target_lab, palette_lab);
        if dist < min_dist {
            min_dist = dist;
            best_mino = mino;
        }
    }

    best_mino
}

/// Extract 10x20 matrix from raw screen pixels given matrix bounding box coordinates
pub fn parse_board_from_pixels(
    pixels: &[u8],
    img_width: u32,
    board_x: u32,
    board_y: u32,
    board_w: u32,
    board_h: u32,
) -> BoardMatrix {
    let mut matrix: BoardMatrix = [[Mino::Empty; BOARD_WIDTH]; BOARD_HEIGHT];
    let cell_w = board_w as f32 / BOARD_WIDTH as f32;
    let cell_h = board_h as f32 / VISIBLE_HEIGHT as f32;

    for row in 0..VISIBLE_HEIGHT {
        for col in 0..BOARD_WIDTH {
            // Sample center 3x3 pixel area inside cell to avoid border gridlines
            let center_x = (board_x as f32 + (col as f32 + 0.5) * cell_w) as u32;
            let center_y = (board_y as f32 + (row as f32 + 0.5) * cell_h) as u32;

            let idx = ((center_y * img_width + center_x) * 4) as usize;
            if idx + 2 < pixels.len() {
                let sampled = RgbColor {
                    r: pixels[idx],
                    g: pixels[idx + 1],
                    b: pixels[idx + 2],
                };
                
                // Matrix rows in game logic: 0 is bottom row, VISIBLE_HEIGHT-1 top row
                let target_row = VISIBLE_HEIGHT - 1 - row;
                matrix[target_row][col] = classify_color(sampled);
            }
        }
    }

    matrix
}
