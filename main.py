#!/usr/bin/env python3
"""
R-TYPE Clone
A horizontal scrolling shooter game inspired by the classic arcade game R-TYPE.

Controls:
- Arrow Keys: Move player
- Z: Normal shot (hold for continuous fire)
- X: Charge shot (hold to charge, release to fire)
- C: Toggle Force position (Front/Back/Detached)
- ESC: Quit game
- R: Restart (when game over)

Features:
- Force orb system with attach/detach mechanics
- Charge shot with 3 levels
- 4 types of enemies with different patterns
- Wave-based enemy spawning
- Power-ups (Force, Speed, Power)
- Visual explosion effects
"""

from game import Game

def main():
    print("=" * 60)
    print("R-TYPE CLONE")
    print("=" * 60)
    print("\nControls:")
    print("  Arrow Keys - Move")
    print("  Z          - Shoot (hold for auto-fire)")
    print("  X          - Charge Shot (hold to charge)")
    print("  C          - Toggle Force (Front/Back/Detached)")
    print("  ESC        - Quit")
    print("\nStarting game...")
    print("=" * 60)

    game = Game()
    game.run()

    print("\nThanks for playing!")

if __name__ == "__main__":
    main()
