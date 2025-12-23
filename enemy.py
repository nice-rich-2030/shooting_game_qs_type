import pygame
import math
from constants import *
from bullet import Bullet

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.active = True
        self.time_alive = 0

        # Set properties based on type
        if enemy_type == ENEMY_TYPE_STRAIGHT:
            self.hp = ENEMY_STRAIGHT_HP
            self.speed = ENEMY_STRAIGHT_SPEED
            self.score = ENEMY_STRAIGHT_SCORE
            self.color = RED
            self.size = 25
            self.shoot_interval = 0  # Doesn't shoot

        elif enemy_type == ENEMY_TYPE_WAVE:
            self.hp = ENEMY_WAVE_HP
            self.speed = ENEMY_WAVE_SPEED
            self.score = ENEMY_WAVE_SCORE
            self.color = GREEN
            self.size = 30
            self.shoot_interval = 120  # Shoots every 2 seconds

        elif enemy_type == ENEMY_TYPE_CHARGE:
            self.hp = ENEMY_CHARGE_HP
            self.speed = ENEMY_CHARGE_SPEED
            self.score = ENEMY_CHARGE_SCORE
            self.color = CYAN
            self.size = 28
            self.shoot_interval = 0  # Doesn't shoot, just charges

        else:  # ENEMY_TYPE_TANK
            self.hp = ENEMY_TANK_HP
            self.speed = ENEMY_TANK_SPEED
            self.score = ENEMY_TANK_SCORE
            self.color = ORANGE
            self.size = 40
            self.shoot_interval = 90  # Shoots every 1.5 seconds

        self.max_hp = self.hp
        self.shoot_cooldown = self.shoot_interval
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        # For wave movement
        self.initial_y = y
        self.wave_amplitude = 50
        self.wave_frequency = 0.05

        # For charge movement
        self.target_y = None

    def update(self, player_y):
        if not self.active:
            return []

        self.time_alive += 1
        bullets = []

        # Movement based on type
        if self.enemy_type == ENEMY_TYPE_STRAIGHT:
            # Simple straight movement
            self.x -= self.speed

        elif self.enemy_type == ENEMY_TYPE_WAVE:
            # Wave pattern movement
            self.x -= self.speed
            self.y = self.initial_y + math.sin(self.time_alive * self.wave_frequency) * self.wave_amplitude

        elif self.enemy_type == ENEMY_TYPE_CHARGE:
            # Charge towards player
            if self.target_y is None:
                self.target_y = player_y

            # Move towards target
            self.x -= self.speed
            if abs(self.y - self.target_y) > 2:
                if self.y < self.target_y:
                    self.y += self.speed * 0.5
                else:
                    self.y -= self.speed * 0.5

        else:  # ENEMY_TYPE_TANK
            # Slow movement
            self.x -= self.speed

        # Keep on screen vertically
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.size))

        # Update rect
        self.rect.x = self.x
        self.rect.y = self.y

        # Deactivate if off screen
        if self.x < -self.size - 50:
            self.active = False

        # Shooting logic
        if self.shoot_interval > 0:
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
            else:
                self.shoot_cooldown = self.shoot_interval
                bullets = self.shoot()

        return bullets

    def shoot(self):
        """Enemy shoots bullets"""
        bullets = []

        if self.enemy_type == ENEMY_TYPE_WAVE:
            # Shoot one bullet to the left
            bullet = Bullet(self.x, self.y + self.size // 2, False)
            bullets.append(bullet)

        elif self.enemy_type == ENEMY_TYPE_TANK:
            # Shoot three bullets in different directions
            for angle_offset in [-20, 0, 20]:
                bullet = Bullet(self.x, self.y + self.size // 2, False)
                # Modify bullet trajectory slightly (simplified)
                bullets.append(bullet)

        return bullets

    def take_damage(self, damage):
        """Enemy takes damage"""
        self.hp -= damage
        if self.hp <= 0:
            self.active = False
            return True  # Enemy destroyed
        return False

    def draw(self, screen):
        if not self.active:
            return

        # Draw enemy based on type
        if self.enemy_type == ENEMY_TYPE_STRAIGHT:
            # Draw as square
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)

        elif self.enemy_type == ENEMY_TYPE_WAVE:
            # Draw as diamond
            center_x = self.x + self.size // 2
            center_y = self.y + self.size // 2
            half_size = self.size // 2
            points = [
                (center_x, center_y - half_size),
                (center_x + half_size, center_y),
                (center_x, center_y + half_size),
                (center_x - half_size, center_y)
            ]
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, WHITE, points, 2)

        elif self.enemy_type == ENEMY_TYPE_CHARGE:
            # Draw as triangle pointing left
            points = [
                (self.x, self.y + self.size // 2),  # Tip
                (self.x + self.size, self.y),  # Top right
                (self.x + self.size, self.y + self.size)  # Bottom right
            ]
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, WHITE, points, 2)

        else:  # ENEMY_TYPE_TANK
            # Draw as large rectangle with details
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 3)
            # Add "armor" lines
            pygame.draw.line(
                screen, WHITE,
                (self.x + 10, self.y + self.size // 2),
                (self.x + self.size - 10, self.y + self.size // 2),
                2
            )

        # Draw HP bar
        if self.hp < self.max_hp:
            bar_width = self.size
            bar_height = 4
            bar_x = self.x
            bar_y = self.y - 8

            # Background
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            # HP
            hp_width = int(bar_width * (self.hp / self.max_hp))
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, hp_width, bar_height))
