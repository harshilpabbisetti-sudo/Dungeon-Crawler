# Dungeon Crawler Stealth Game

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/library-Pygame-green?logo=pygame&logoColor=white)
![Genre](https://img.shields.io/badge/genre-Stealth%20%2F%20Dungeon%20Crawler-orange)

A top-down procedural dungeon stealth game built using **Python and Pygame**. Navigate through a dynamically generated labyrinth, evade intelligent enemies with advanced vision and hearing systems, utilize environmental hiding spots, and race against the clock to find the underground exit.

---

## 🎮 Gameplay & Controls

### Objective
Your goal is to navigate the dungeon, avoid detection by patrolling monsters, and reach the **exit ladder** located in the center of one of the rooms to escape. 

### Controls
*   **Movement:** `W`, `A`, `S`, `D` or **Arrow Keys** (Move freely in 8 directions)
*   **Sprint:** Hold **Left Option / Alt** key (Increases speed but expands your noise footprint)
*   **Hide / Interact:** `F` key (Toggle hiding inside objects like barrels and chests when adjacent to them, or to exit them)
*   **Restart Game:** `Spacebar` (Accessible on the Win/Game-Over screens)

---

## 🛠️ Installation & Setup

### Prerequisites
*   **Python:** Version `3.10` or higher is recommended.
*   **Pygame:** Version `2.0.0` or higher.

### Quick Start Guide

1. **Clone or Navigate to the Repository:**
   ```bash
   cd "Dungeon Crawler"
   ```

2. **Install Dependencies:**
   Since the project only requires Pygame, install it directly using `pip`:
   ```bash
   pip install pygame
   ```

3. **Run the Game:**
   Execute the main entry script from the project root directory:
   ```bash
   python code/main.py
   ```

---

## 🏗️ Project Architecture

```text
📁 Dungeon Crawler/
├── 📁 audio/              # Sound effects and background tracks
├── 📁 code/               # Core Python application logic
│   ├── 📄 astar.py        # A* Pathfinding algorithm
│   ├── 📄 dungeon_gen.py  # Procedural map generation (BSP)
│   ├── 📄 monster.py      # Enemy AI state machine & vision cone raycasting
│   ├── 📄 player.py       # Player movement, hiding, and sound mechanics
│   └── 📄 main.py         # Main game entry point and loop
├── 📁 font/               # TrueType text font styles
├── 📁 graphics/           # Entity animation frames, obstacles, and map tiles
├── 📄 README.md           # Project documentation and guide
└── 📄 requirements.txt    # Project external dependencies
```

---

## 🧠 Technical Architecture & Features

### 🏢 1. Procedural Dungeon Generation
Maps are dynamically constructed using a **Binary Space Partitioning (BSP)** algorithm combined with sequential room connectivity logic located in `code/dungeon_gen.py`.
*   Guarantees a valid, fully connected path from the player spawn point to the exit.
*   Distributes hiding containers and obstacle colliders throughout rooms dynamically.
*   Spawns enemies intelligently across various rooms to ensure balanced difficulty.

### 👁️ 2. Advanced Raycasted Vision System
Enemies possess explicit vision cones computed using a 2D segment-based raycasting engine (`code/monster.py`).
*   Vision cones account for the enemy's facing direction, field of view angle, and viewing distance limit.
*   Rays intersect precisely with static walls and obstacle edges, allowing objects to dynamically cast shadows and block line of sight.
*   Vision cones are color-coded and rendered on screen so players can visually infer and exploit enemy blindspots.

### 🔊 3. Dynamic Sound & Hearing System
Player actions dynamically alter their sound footprint (`_update_sound_radius` in `code/player.py`).
*   **Hiding:** Yields zero sound.
*   **Walking:** Creates a standard hearing radius.
*   **Sprinting:** Generates a significantly larger sound radius.
*   If an enemy is within range of a sound event, they transition to an **Inspect** state and navigate directly to the noise origin.

### 🤖 4. Triple-State Enemy AI (Roam, Inspect, Chase)
Enemies operate on a finite state machine using an **A\* Pathfinding algorithm** (`code/astar.py`) for smart navigation:
1.  **Roam:** Patrolls rooms or corridors randomly or along semi-guided directions.
2.  **Inspect:** Investigates sound cues or recently lost player positions using optimized pathfinding.
3.  **Chase:** Enters a high-alert direct pursuit state when the player is seen. If the player breaks line of sight and successfully hides while outside the vision cone, the enemy will search the last seen area before returning to a patrol.

### 🏆 5. Extra Features
*   **Multiple Enemy Types:** 6 distinct monster types (Bee, Goblin, Mouse, Rider, Slime, Wolf) loaded with unique stats from `code/monsters.json`.
*   **Fog of War:** Dynamic rendering with a persistent reveal shroud and flashlight field-of-view tracking around the player.
*   **Stopwatch/Timer:** Real-time run tracking displayed during gameplay and recorded upon success or failure.

---

## 🤝 How to Contribute

Contributions are always welcome! If you would like to help improve this game, feel free to fork this repository, create a new feature branch, and submit a Pull Request (PR) with your proposed changes or bug fixes.

---

## 🎨 Asset Attributions

All graphical sprites and external resources used in this project are high-quality open-source assets obtained from the following creators:

*   **Enemy Sprite Packs:** 
    *   [Free Enemy Pixel Pack for Top-Down Defense by Free Game Assets](https://free-game-assets.itch.io/free-enemy-pixel-pack-for-top-down-defense)
    *   [Free Field Enemies Pixel Art by Free Game Assets](https://free-game-assets.itch.io/free-field-enemies-pixel-art-for-tower-defense)
    *   [Other Assets](https://itch.io)
*   **Dungeon Tilesets:**
    *   [Top-Down Dungeon Tiles by jnur](https://jnur.itch.io/top-down-dungeon-tiles)
    *   [Dungeon Tileset 2 by SavvyCow](https://savvycow.itch.io/dungeon-tileset-2)
*   **General Audio & Inspiration:**
    *   [OpenGameArt.org](https://opengameart.org/)

---

## 📄 License & Submissions
Developed by **Harshil Pabbisetti**
