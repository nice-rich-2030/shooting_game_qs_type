import pygame
from constants import *

class Bullet:
    def __init__(self, x, y, is_player_bullet=True, charge_level=0):
        self.x = x
        self.y = y
        self.is_player_bullet = is_player_bullet
        self.charge_level = charge_level
        self.active = True

        if is_player_bullet:
            # Player bullet properties
            if charge_level == 0:
                # Normal bullet
                self.width = BULLET_WIDTH
                self.height = BULLET_HEIGHT
                self.speed = BULLET_SPEED
                self.damage = BULLET_DAMAGE
                self.pierce_count = 1
                self.color = WHITE
            elif charge_level == 1:
                # Charge level 1
                self.width = BULLET_WIDTH * CHARGE_LEVEL_1_SIZE
                self.height = BULLET_HEIGHT * CHARGE_LEVEL_1_SIZE
                self.speed = BULLET_SPEED
                self.damage = CHARGE_LEVEL_1_DAMAGE
                self.pierce_count = 1
                self.color = WHITE
            elif charge_level == 2:
                # Charge level 2
                self.width = BULLET_WIDTH * CHARGE_LEVEL_2_SIZE
                self.height = BULLET_HEIGHT * CHARGE_LEVEL_2_SIZE
                self.speed = BULLET_SPEED
                self.damage = CHARGE_LEVEL_2_DAMAGE
                self.pierce_count = CHARGE_LEVEL_2_PIERCE
                self.color = YELLOW
            else:
                # Charge level 3 (max)
                self.width = BULLET_WIDTH * CHARGE_LEVEL_3_SIZE
                self.height = BULLET_HEIGHT * CHARGE_LEVEL_3_SIZE
                self.speed = BULLET_SPEED
                self.damage = CHARGE_LEVEL_3_DAMAGE
                self.pierce_count = CHARGE_LEVEL_3_PIERCE
                self.color = RED
        else:
            # Enemy bullet
            self.width = ENEMY_BULLET_WIDTH
            self.height = ENEMY_BULLET_HEIGHT
            self.speed = -ENEMY_BULLET_SPEED  # Move left
            self.damage = 1
            self.pierce_count = 1
            self.color = ORANGE

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        if not self.active:
            return

        # Move bullet
        if self.is_player_bullet:
            self.x += self.speed
        else:
            self.x += self.speed

        self.rect.x = self.x
        self.rect.y = self.y

        # Deactivate if off screen
        if self.x > SCREEN_WIDTH + 50 or self.x < -50:
            self.active = False

    def hit(self):
        """Called when bullet hits something"""
        self.pierce_count -= 1
        if self.pierce_count <= 0:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return

        pygame.draw.rect(screen, self.color, self.rect)

        # Add glow effect for charge bullets
        if self.is_player_bullet and self.charge_level > 0:
            glow_rect = pygame.Rect(
                self.rect.x - 2,
                self.rect.y - 2,
                self.rect.width + 4,
                self.rect.height + 4
            )
            glow_color = tuple(min(255, c + 50) for c in self.color)
            pygame.draw.rect(screen, glow_color, glow_rect, 2)
