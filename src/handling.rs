use std::time::Duration;
use crate::types::*;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Direction {
    None,
    Left,
    Right,
}

#[derive(Debug, Clone)]
pub struct InputState {
    pub left_pressed: bool,
    pub right_pressed: bool,
    pub soft_drop_pressed: bool,
}

pub struct HandlingEngine {
    pub config: HandlingConfig,
    pub active_dir: Direction,
    pub das_timer: Duration,
    pub arr_timer: Duration,
    pub dcd_timer: Duration,
    pub soft_drop_accumulator: Duration,
}

impl HandlingEngine {
    pub fn new(config: HandlingConfig) -> Self {
        Self {
            config,
            active_dir: Direction::None,
            das_timer: Duration::ZERO,
            arr_timer: Duration::ZERO,
            dcd_timer: Duration::ZERO,
            soft_drop_accumulator: Duration::ZERO,
        }
    }

    /// Process input delta and yield board horizontal movement steps
    pub fn update(&mut self, dt: Duration, inputs: &InputState) -> i32 {
        let mut x_shift = 0;

        // Determine active direction based on recent key press
        let new_dir = match (inputs.left_pressed, inputs.right_pressed) {
            (true, false) => Direction::Left,
            (false, true) => Direction::Right,
            _ => Direction::None,
        };

        // Direction change / DAS Cut Delay (DCD) handling
        if new_dir != self.active_dir {
            if new_dir != Direction::None {
                // Immediate initial shift upon press
                x_shift += if new_dir == Direction::Left { -1 } else { 1 };
                self.das_timer = Duration::ZERO;
                self.arr_timer = Duration::ZERO;
                self.dcd_timer = self.config.dcd;
            }
            self.active_dir = new_dir;
            return x_shift;
        }

        if self.active_dir == Direction::None {
            return 0;
        }

        // Apply DCD if present
        if self.dcd_timer > Duration::ZERO {
            if dt >= self.dcd_timer {
                let remaining_dt = dt - self.dcd_timer;
                self.dcd_timer = Duration::ZERO;
                self.das_timer += remaining_dt;
            } else {
                self.dcd_timer -= dt;
                return 0;
            }
        } else {
            self.das_timer += dt;
        }

        // DAS check
        if self.das_timer >= self.config.das {
            if self.config.arr == Duration::ZERO {
                // Instant ARR: Move piece all the way to wall (represented by infinity steps)
                x_shift = if self.active_dir == Direction::Left { -BOARD_WIDTH as i32 } else { BOARD_WIDTH as i32 };
            } else {
                // Accumulate ARR steps
                self.arr_timer += dt;
                while self.arr_timer >= self.config.arr {
                    x_shift += if self.active_dir == Direction::Left { -1 } else { 1 };
                    self.arr_timer -= self.config.arr;
                }
            }
        }

        x_shift
    }

    /// Update lock delay timer given piece grounding state
    pub fn update_lock_delay(
        &mut self,
        dt: Duration,
        piece: &mut ActivePiece,
        is_grounded: bool,
    ) -> bool {
        if !is_grounded {
            piece.lock_delay_accumulator = Duration::ZERO;
            return false;
        }

        piece.lock_delay_accumulator += dt;
        piece.lock_delay_accumulator >= self.config.lock_delay
    }

    /// Reset lock delay when piece moves or rotates if allowed
    pub fn reset_lock_delay_if_allowed(&self, piece: &mut ActivePiece) {
        if piece.lock_resets_used < self.config.max_lock_resets {
            piece.lock_delay_accumulator = Duration::ZERO;
            piece.lock_resets_used += 1;
        }
    }
}
