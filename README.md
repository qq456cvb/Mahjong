# Mahjong

A four-player Mahjong game written in Python/pygame, with a Monte-Carlo Tree Search (MCTS) AI running in a multi-process C++ engine.

## Features

- **Playable GUI**: you play the South seat against three computer opponents, with click-to-select tiles for discarding, and support for chow (吃), pung (碰), and win (和) responses.
- **MCTS AI**: `MCPlayer` picks actions by simulating random playouts with `mc_search`, implemented in C++ (`c_src/`) and exposed to Python through [pybind11](https://github.com/pybind/pybind11) with multi-process rollouts. A pure-Python MCTS reference lives in `montecarlo.py`.
- **Fast win detection**: winning hands are detected with a precomputed lookup table (`complete.pickle`, 9,362 hand keys) derived from the classic `AgariIndex` algorithm (`AgariIndex.java` is kept for reference), instead of enumerating melds at runtime.
- **Headless environment**: `pyenv.py` runs games entirely in the terminal (MCTS vs. random players), useful for benchmarking AI strength without the GUI.

## Code Layout

| Path | Description |
|---|---|
| `controller.py` | Game loop and rules for the pygame GUI version (entry point) |
| `pyenv.py` | Terminal-only game environment with `RandomPlayer` / `MCPlayer` (entry point) |
| `players.py` | Player logic: hand management, chow/pung/win checks via the lookup table; the GUI `AIPlayer` uses a simple discard policy |
| `graphics.py`, `sprites.py`, `resource.py` | pygame rendering, tile sprites, asset loading |
| `montecarlo.py` | Pure-Python MCTS reference implementation (superseded by the C++ engine) |
| `c_src/` | C++ MCTS engine (`mctree.cpp`, `player.cpp`) and pybind11 bindings (`export.cpp`) |
| `complete.pickle` | Precomputed winning-hand key table loaded at startup |
| `AgariIndex.java` | Original Java source of the winning-hand table generator (reference only) |
| `tiles/` | Tile face images |

## Setup

Requires Python 3 with `pygame` and `numpy`, plus CMake, pybind11, and a C++14 compiler for the AI engine.

1. Install Python dependencies:

```bash
pip install pygame numpy pybind11
```

2. Build the C++ MCTS module into `build/`:

```bash
mkdir build && cd build
cmake ..
cmake --build . --config Release
```

The Python code imports the compiled module as `build.Release.clib` (MSVC layout); on Linux/macOS, place the built `clib` extension under `build/` and adjust the import accordingly.

## Play

```bash
python controller.py   # GUI game: you (South) vs. 3 computer players
python pyenv.py        # terminal simulation: MCTS vs. random players
```

In the GUI, click tiles to raise/select them and discard; prompts appear when you can chow, pung, or declare a win. MCTS strength can be tuned via `NUM_PROCS` and `NUM_SEARCH` at the top of `pyenv.py`.

## Notes

- The game implements a simplified Chinese ruleset over the standard 34 tile types (136 tiles), with chow/pung/win interactions.
- UI text is in Chinese.
