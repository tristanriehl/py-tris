use std::time::Duration;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Mino {
    Empty,
    I,
    J,
    L,
    O,
    S,
    T,
    Z,
    Garbage,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Rotation {
    R0 = 0,   // Spawn
    R90 = 1,  // Clockwise (R)
    R180 = 2, // 180 degrees (2)
    R270 = 3, // Counter-clockwise (L)
}

impl Rotation {
    pub fn rotate_cw(self) -> Self {
        match self {
            Self::R0 => Self::R90,
            Self::R90 => Self::R180,
            Self::R180 => Self::R270,
            Self::R270 => Self::R0,
        }
    }

    pub fn rotate_ccw(self) -> Self {
        match self {
            Self::R0 => Self::R270,
            Self::R90 => Self::R0,
            Self::R180 => Self::R90,
            Self::R270 => Self::R180,
        }
    }

    pub fn rotate_180(self) -> Self {
        match self {
            Self::R0 => Self::R180,
            Self::R90 => Self::R270,
            Self::R180 => Self::R0,
            Self::R270 => Self::R90,
        }
    }
}

pub const BOARD_WIDTH: usize = 10;
pub const BOARD_HEIGHT: usize = 40; // 20 visible + 20 buffer
pub const VISIBLE_HEIGHT: usize = 20;

pub type BoardMatrix = [[Mino; BOARD_WIDTH]; BOARD_HEIGHT];

#[derive(Debug, Clone)]
pub struct HandlingConfig {
    pub das: Duration,      // Delayed Auto Shift (e.g. 133ms)
    pub arr: Duration,      // Auto Repeat Rate (0ms = instant)
    pub sdf: f32,           // Soft Drop Factor (100.0 = infinity)
    pub dcd: Duration,      // DAS Cut Delay (0ms - 50ms)
    pub lock_delay: Duration, // Lock delay (500ms)
    pub max_lock_resets: u32,  // Max move resets before forcing lock (15)
}

impl Default for HandlingConfig {
    fn default() -> Self {
        Self {
            das: Duration::from_millis(133),
            arr: Duration::from_millis(0),
            sdf: 40.0,
            dcd: Duration::from_millis(0),
            lock_delay: Duration::from_millis(500),
            max_lock_resets: 15,
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct ActivePiece {
    pub mino: Mino,
    pub x: i32,
    pub y: i32,
    pub rotation: Rotation,
    pub lock_delay_accumulator: Duration,
    pub lock_resets_used: u32,
    pub lowest_y: i32,
}

// Kick table offset vectors: (dx, dy)
pub type KickTable = &'static [[(i32, i32); 5]];

// Standard SRS Kick Tables for J, L, S, T, Z
pub static JLSTZ_KICKS_CW: [((Rotation, Rotation), [(i32, i32); 5]); 4] = [
    ((Rotation::R0, Rotation::R90), [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)]),
    ((Rotation::R90, Rotation::R180), [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)]),
    ((Rotation::R180, Rotation::R270), [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]),
    ((Rotation::R270, Rotation::R0), [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)]),
];

// SRS Kick Tables for I piece
pub static I_KICKS_CW: [((Rotation, Rotation), [(i32, i32); 5]); 4] = [
    ((Rotation::R0, Rotation::R90), [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)]),
    ((Rotation::R90, Rotation::R180), [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]),
    ((Rotation::R180, Rotation::R270), [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)]),
    ((Rotation::R270, Rotation::R0), [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)]),
];

// SRS 180-degree Kick Tables
static KICKS_180: [((Rotation, Rotation), [(i32, i32); 6]); 4] = [
    ((Rotation::R0, Rotation::R180), [(0, 0), (0, 1), (1, 1), (-1, 1), (1, 0), (-1, 0)]),
    ((Rotation::R90, Rotation::R270), [(0, 0), (1, 0), (1, 2), (1, 1), (0, 1), (0, 2)]),
    ((Rotation::R180, Rotation::R0), [(0, 0), (0, -1), (-1, -1), (1, -1), (-1, 0), (1, 0)]),
    ((Rotation::R270, Rotation::R90), [(0, 0), (-1, 0), (-1, 2), (-1, 1), (0, 1), (0, 2)]),
];
