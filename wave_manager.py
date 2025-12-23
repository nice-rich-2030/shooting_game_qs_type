import random
from constants import *
from enemy import Enemy

class WaveManager:
    def __init__(self):
        self.game_time = 0
        self.spawn_timer = 0
        self.current_wave = 1
        self.enemies_spawned_this_wave = 0

    def update(self):
        self.game_time += 1
        self.spawn_timer += 1

        # Update current wave based on time
        if self.game_time < WAVE_1_END:
            new_wave = 1
        elif self.game_time < WAVE_2_END:
            new_wave = 2
        elif self.game_time < WAVE_3_END:
            new_wave = 3
        else:
            new_wave = 4

        # Reset counter when wave changes
        if new_wave != self.current_wave:
            self.current_wave = new_wave
            self.enemies_spawned_this_wave = 0

    def should_spawn_enemy(self):
        """Check if it's time to spawn an enemy"""
        # Vary spawn interval slightly
        spawn_interval = ENEMY_SPAWN_INTERVAL + random.randint(-20, 20)

        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0
            return True
        return False

    def spawn_enemy(self):
        """Spawn an enemy based on current wave"""
        if not self.should_spawn_enemy():
            return None

        # Random Y position
        y = random.randint(50, SCREEN_HEIGHT - 100)
        x = SCREEN_WIDTH + 50

        enemy_type = None

        # Wave 1: Only straight enemies
        if self.current_wave == 1:
            if self.enemies_spawned_this_wave < 10:
                enemy_type = ENEMY_TYPE_STRAIGHT
                self.enemies_spawned_this_wave += 1

        # Wave 2: Wave pattern enemies
        elif self.current_wave == 2:
            if self.enemies_spawned_this_wave < 8:
                enemy_type = ENEMY_TYPE_WAVE
                self.enemies_spawned_this_wave += 1

        # Wave 3: Charge enemies + some straight
        elif self.current_wave == 3:
            if self.enemies_spawned_this_wave < 10:
                if random.random() < 0.6:
                    enemy_type = ENEMY_TYPE_CHARGE
                else:
                    enemy_type = ENEMY_TYPE_STRAIGHT
                self.enemies_spawned_this_wave += 1

        # Wave 4: All types mixed, infinite
        else:
            rand = random.random()
            if rand < 0.3:
                enemy_type = ENEMY_TYPE_STRAIGHT
            elif rand < 0.5:
                enemy_type = ENEMY_TYPE_WAVE
            elif rand < 0.8:
                enemy_type = ENEMY_TYPE_CHARGE
            else:
                enemy_type = ENEMY_TYPE_TANK

        if enemy_type is not None:
            return Enemy(x, y, enemy_type)

        return None

    def get_wave_text(self):
        """Get text describing current wave"""
        return f"WAVE {self.current_wave}"
