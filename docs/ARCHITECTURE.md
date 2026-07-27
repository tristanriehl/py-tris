# Four-Tris Engine Architecture & Sub-Millisecond Input Pipeline

## 1. Sub-Millisecond Precision Timing Engine
To achieve TETR.IO-accurate handling and eliminate OS-level key repeat jitter, the engine decouples high-frequency logical input sampling from screen rendering.

```
       +-------------------------------------------------------+
       |           High-Frequency Loop (1000Hz Ticks)          |
       |  - Read raw OS keyboard bitmask                       |
       |  - Update DAS / ARR / SDF / DCD state machine          |
       |  - Apply piece movement & collision logic             |
       +-------------------------------------------------------+
                                   |
                                   v
       +-------------------------------------------------------+
       |             Renderer Loop (60Hz / 120Hz / Metal)      |
       |  - Interpolate active piece position (if required)    |
       |  - Render Board matrix, Ghost Piece, Next Queue, Hold |
       +-------------------------------------------------------+
```

### Key Loop Principles
1. **Monotonic Timing (`std::time::Instant`)**: All timers for DAS, ARR, SDF, DCD, and Lock Delay use high-precision monotonic clock deltas (`dt`).
2. **Deterministic Ticks**: Input state updates run at 1000Hz fixed ticks (1ms interval) or variable sub-ms micro-deltas.
3. **OS Jitter Avoidance**: Native OS key-repeat events are disabled for movement actions. The engine captures `KeyDown` and `KeyUp` timestamp events and manages auto-repeat completely internally.

## 2. Decoupled State & Practice Mode Undo Engine
* **`GameState`** holds the current playfield, active piece state, 7-bag RNG state, and handling parameters.
* **`UndoBuffer`**: Every hard drop, hold, or manual edit pushes a delta snapshot into an infinite double-ended queue (`VecDeque<GameState>`), allowing instantaneous zero-latency undo/redo operations.
