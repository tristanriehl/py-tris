mod handling;
mod types;
mod vision;

use std::thread;
use std::time::{Duration, Instant};
use handling::{HandlingEngine, InputState};
use types::{ActivePiece, BoardMatrix, HandlingConfig, Mino, Rotation, BOARD_HEIGHT, BOARD_WIDTH, VISIBLE_HEIGHT};

fn render_board_ascii(board: &BoardMatrix, active: &ActivePiece) {
    print!("\x1B[2J\x1B[1;1H"); // Clear screen ansi code
    println!("=== FOUR-TRIS TETR.IO PRACTICE ENGINE ===");
    println!("+----------+");
    for y in (0..VISIBLE_HEIGHT).rev() {
        print!("|");
        for x in 0..BOARD_WIDTH {
            let is_active = active.x <= x as i32 
                && (x as i32) < active.x + 3 
                && active.y <= y as i32 
                && (y as i32) < active.y + 3;

            if is_active && active.mino != Mino::Empty {
                print!("O");
            } else {
                match board[y][x] {
                    Mino::Empty => print!("."),
                    Mino::Garbage => print!("X"),
                    _ => print!("#"),
                }
            }
        }
        println!("|");
    }
    println!("+----------+");
    println!("Piece Position: ({}, {})", active.x, active.y);
}

fn main() {
    let config = HandlingConfig::default();
    let mut engine = HandlingEngine::new(config);
    let board: BoardMatrix = [[Mino::Empty; BOARD_WIDTH]; BOARD_HEIGHT];

    let mut active = ActivePiece {
        mino: Mino::T,
        x: 3,
        y: 18,
        rotation: Rotation::R0,
        lock_delay_accumulator: Duration::ZERO,
        lock_resets_used: 0,
        lowest_y: 18,
    };

    let inputs = InputState {
        left_pressed: false,
        right_pressed: false,
        soft_drop_pressed: true,
    };

    let mut last_tick = Instant::now();

    for _ in 0..20 {
        let now = Instant::now();
        let dt = now.duration_since(last_tick);
        last_tick = now;

        let _shift = engine.update(dt, &inputs);
        if active.y > 0 {
            active.y -= 1;
        }

        render_board_ascii(&board, &active);
        thread::sleep(Duration::from_millis(100));
    }
}
