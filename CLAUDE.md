# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

R-TYPE clone - a horizontal scrolling shooter game inspired by the 1987 Irem arcade game. Built with Pygame using simple geometric shapes for graphics.

## Running the Game

```bash
# Install dependencies
pip install pygame

# Run the game
python main.py
```

## Architecture

### Game Loop Structure

The game follows a classic game loop pattern in `game.py`:
1. **Event Handling** (`handle_events()`) - Process keyboard input and window events
2. **Update** (`update()`) - Update all game objects, collision detection, wave management
3. **Draw** (`draw()`) - Render all objects and UI to screen
4. Runs at 60 FPS (controlled by `self.clock.tick(FPS)`)

### Core Game Systems

**Force Orb System** (R-TYPE's signature mechanic):
- Three states: ATTACHED_FRONT (0), ATTACHED_BACK (1), DETACHED (2)
- Force absorbs enemy bullets when active (checked in collision detection)
- Player can toggle states with C key
- Force must be acquired via powerup before becoming active
- When attached, Force position is calculated relative to player position
- Force shoots bullets synchronized with player

**Charge Shot System**:
- Uses frame-based timing (not real time)
- Three charge levels at 30, 60, 90 frames (0.5s, 1.0s, 1.5s at 60 FPS)
- Player class tracks `charging`, `charge_time`, and `charge_level`
- Charge bullets have different sizes, damage, and pierce counts
- Released on key release in `player.update()` by returning bullet list

**Wave Management**:
- Time-based progression using `game_time` counter (frames)
- Four waves with increasing difficulty at 1800, 3600, 5400 frames (30s, 60s, 90s)
- WaveManager handles enemy spawning logic with type distribution per wave
- Enemy spawn timing varies with random interval adjustment

**Collision Detection**:
- All collision checks happen in `game.check_collisions()`
- Order matters: Force bullet absorption checked before player hit
- Enemy destruction triggers score, explosions, and powerup drops (20% chance)
- Player invincibility handled in Player class with blink timer

### Object Lifecycle Pattern

All game objects follow this pattern:
- Have an `active` boolean flag
- Update method modifies state
- Objects filtered by active status: `self.enemies = [e for e in self.enemies if e.active]`
- Deactivated when off-screen or destroyed

### Entity Classes

**Player** (`player.py`):
- Manages movement, shooting, charging, invincibility
- `update()` returns charge bullets when released
- `shoot()` returns normal bullets (called externally)
- Holds `power_level` and `speed` for upgrades

**Force** (`force.py`):
- Starts inactive, must be activated via `activate(x, y)`
- Position calculated in `update()` based on state and player position
- Has own shooting cooldown independent of player

**Enemy** (`enemy.py`):
- Four types with different movement patterns in `update()`:
  - STRAIGHT: Simple linear movement
  - WAVE: Sine wave using `time_alive * wave_frequency`
  - CHARGE: Locks target Y position, approaches it
  - TANK: Slow movement, shoots 3-direction spread
- `update()` returns list of bullets fired

**Bullet** (`bullet.py`):
- Constructor sets properties based on `is_player_bullet` and `charge_level`
- Pierce count decrements on hit; bullet deactivates when pierce_count <= 0
- Player bullets move right (+speed), enemy bullets move left (-speed)

### Constants and Tuning

All game balance values in `constants.py`:
- Frame-based timings (multiply by 60 for seconds)
- Enemy stats organized by type suffix (HP, SPEED, SCORE)
- Force states are integer constants (0, 1, 2)
- Wave transitions defined by frame counts

## Key Implementation Details

**Frame-based timing**: All timers use frame counts, not milliseconds. Convert: `frames = seconds * 60`

**Bullet synchronization**: When player shoots (normal or charge), Force also shoots if active. This is handled in `game.py` by calling both `player.shoot()` and `force.shoot()`.

**Powerup drops**: Generated in collision detection when enemy destroyed, not in Enemy class itself.

**Game restart**: Pressing R on game over calls `self.__init__()` to reset all state.

**Continuous fire**: Z key checked both in event handler (single press) and in update (continuous hold).

**Visual feedback**:
- Charge level shown via player glow color and charge gauge
- Invincibility shown via blink effect (timer % 10 < 5)
- Force state indicated by arrow direction inside orb

## Common Modifications

**Adjusting difficulty**:
- Modify enemy HP/speed in constants.py
- Change ENEMY_SPAWN_INTERVAL for spawn rate
- Adjust wave transition times (WAVE_X_END values)

**Adding enemy types**:
1. Add ENEMY_TYPE_X constant
2. Add stats constants (HP, SPEED, SCORE)
3. Implement movement pattern in Enemy.update()
4. Add to WaveManager spawn logic

**Tuning charge shot**:
- Modify CHARGE_LEVEL_X_TIME for charge duration
- Adjust SIZE, DAMAGE, PIERCE constants for power level
- Color changes handled in bullet.py constructor

**Balancing Force**:
- FORCE_ATTACH_DISTANCE controls offset from player
- FORCE_DETACHED_SPEED controls drift speed when free
- Bullet absorption is automatic when Force is active
