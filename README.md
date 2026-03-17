# Chess Puzzle Solving 

<div align="center">
    <a href="https://www.python.org/downloads/release/python-31213/">
        <img src="https://img.shields.io/badge/Python-3.12%2B-blue" height="20" alt="Python 3.12+">
    </a>
    <a href="https://www.pygame.org/news">
        <img src="https://img.shields.io/badge/Pygame-2.6.1-green" height="20" alt="Pygame 2.6.1">
    </a>
    <a href="https://numpy.org/install/">
        <img src="https://img.shields.io/badge/NumPy-2.4.2-blue" height="20" alt="NumPy 2.4.2">
    </a>
    <h3>Chess Puzzle Solving - inspired by <a href="https://www.puzzle-chess.com/">Puzzle Chess</a></h3>
</div>
A Pygame-based chess puzzle game inspired by traditional chess mechanics but designed with unique, challenging puzzle modes. CPS includes a built-in map creator and real-time visualization of pathfinding algorithms like A*, BFS, and DFS solving the board.

## 🌟 Features

* **Three Unique Game Modes:**
    * **Ranger Mode:** Only white pieces are used. Standard chess movement rules apply, and every move must be a capture.
    * **Melee Mode:** Alternating turns between white and black pieces, requiring continuous captures until one piece remains.
    * **Solo Mode:** A restrictive mode where only white pieces are used, the King cannot be captured, and every piece can only move a maximum of two times.
* **Built-in Map Creator:** Design, test, and save your own custom puzzles. The creator includes an algorithmic solvability check before saving.
* **Algorithm Visualizer:** Watch search algorithms (A*, BFS, DFS) solve the puzzles in real-time right on the board.
* **Customizable Settings:** Adjust target FPS, play speed, and algorithm search animation duration.

## 🛠️ Installation

1.  **Install dependencies:**
    Ensure you have Python 3.x installed, 3.12+ is recommended.
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the game:**
    ```bash
    python main.py
    ```

## 🎮 How to Play

1.  Launch the game to access the main menu.
2.  Select a puzzle mode: **Ranger**, **Melee**, or **Solo**.
3.  Click and drag a piece to valid capture squares highlighted on the board.
4.  If you get stuck, use the **A***, **BFS**, or **DFS** buttons on the right panel to let the AI find the solution for you. Click the "Play" button next to the algorithm to watch the winning sequence.
5.  Want to build your own? Click **Map Creator** from the main menu, place your pieces, test the board, and save it to the database.

## 🧠 Algorithms Implemented

The game models the board as a state-space graph to evaluate winning paths. 
* **A\* Search (A\*):** Uses a sophisticated heuristic combining piece count with an "Island Detection" connectivity graph ($h = 65 \times (islands - 1) + pieces\_count$). It builds an undirected graph of valid captures to count isolated groups of pieces (islands), applying a massive penalty to disconnected boards. **The more islands there are, the higher the penalty**.
* **Breadth-First Search (BFS):** Explores all possible capture sequences level by level.
* **Depth-First Search (DFS):** Dives deep into specific capture sequences until it hits a dead end or solves the board.

## 📁 Project Structure

```text
├── assets/                 # Static assets for the game
│   ├── images/app/         # UI icons, buttons, logos, and background images
│   └── images/pieces/      # Chess piece sprites (black and white variants)
│
├── data/                   # Game data, settings, and saved puzzles
│   ├── puzzle_info.json    # Core rules and descriptions for puzzle modes
│   ├── user_settings.json  # Saved user preferences (FPS, animation speeds)
│   ├── chess_melee/        # Saved custom maps for Melee mode
│   ├── chess_ranger/       # Saved custom maps for Ranger mode
│   └── chess_solo/         # Saved custom maps for Solo mode
│
├── src/                    # Main source code directory
│   ├── scene_manager.py    # Handles transitions between different game screens
│   │
│   ├── algorithms/         # Pathfinding and puzzle-solving AI
│   │   ├── algorithm.py    # Base solver class
│   │   ├── Astar.py        # A* Search algorithm implementation
│   │   ├── BFS.py          # Breadth-First Search implementation
│   │   └── DFS.py          # Depth-First Search implementation
│   │
│   ├── entities/           # Core chess logic and board mechanics
│   │   ├── chess.py        # Board state, movement validation, and mode-specific rules
│   │   └── figure.py       # Chess piece classes and their movement patterns
│   │
│   ├── scenes/             # Individual game screens/views
│   │   ├── map_creator.py  # Map editor and solvability checker
│   │   ├── menu.py         # Main menu and mode selection
│   │   ├── puzzle.py       # Active gameplay screen and algorithm visualizer
│   │   ├── scene.py        # Base Scene class
│   │   └── settings.py     # User settings configuration screen
│   │
│   ├── ui/                 # Reusable user interface components
│   │   ├── algorithm_handler.py # Manages algorithm execution and playback queues
│   │   └── element.py      # Buttons, sliders, toggles, and label boxes
│   │
│   └── utils/              # Helper functions
│       └── asset_loading.py# Image loading and colorization utilities
```
* `src/entities/`: Contains the logic for the chess pieces (`figure.py`) and the board rules for different modes (`chess.py`).
* `src/algorithms/`: Contains the pathfinding solvers like `Astar.py`.
* `src/scenes/`: Houses the different UI screens (`menu.py`, `puzzle.py`, `map_creator.py`, `settings.py`).
* `data/`: Stores the saved puzzle maps in JSON format.

## 🤝 Contributing

* Contributions, issues, and feature requests are welcome! Feel free to check the issues page. If you want to add new puzzle modes or optimize the search algorithms, please open a pull request.

## 👤 Author

* **Nguyễn Tuấn Long** 
* **Nguyễn Trần Nhật Châu**