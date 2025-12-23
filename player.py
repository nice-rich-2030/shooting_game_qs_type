import pygame
from constants import *
from bullet import Bullet

class Player:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.lives = PLAYER_MAX_LIVES
        self.power_level = 1

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Shooting
        self.shoot_cooldown = 0
        self.shoot_delay = 10  # frames between shots

        # Charge shot
        self.charging = False
        self.charge_time = 0
        self.charge_level = 0

        # Invincibility
        self.invincible = False
        self.invincible_timer = 0
        self.blink_timer = 0

    def update(self, keys):
        # Movement
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed

        # Keep player on screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

        self.rect.x = self.x
        self.rect.y = self.y

        # Update cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Update invincibility
        if self.invincible:
            self.invincible_timer -= 1
            self.blink_timer += 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.blink_timer = 0

        # Charge shot logic
        if keys[pygame.K_x]:
            self.charging = True
            self.charge_time += 1

            # Determine charge level
            if self.charge_time >= CHARGE_LEVEL_3_TIME:
                self.charge_level = 3
            elif self.charge_time >= CHARGE_LEVEL_2_TIME:
                self.charge_level = 2
            elif self.charge_time >= CHARGE_LEVEL_1_TIME:
                self.charge_level = 1
            else:
                self.charge_level = 0
        else:
            # Release charge shot
            if self.charging and self.charge_level > 0:
                bullets = [self.create_charge_bullet()]
                self.charge_time = 0
                self.charge_level = 0
                self.charging = False
                return bullets

            self.charging = False
            self.charge_time = 0
            self.charge_level = 0

        return []

    def shoot(self):
        """Shoot normal bullets (Z key)"""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_delay
            return [Bullet(self.x + self.width, self.y + self.height // 2 - 2, True, 0)]
        return []

    def create_charge_bullet(self):
        """Create a charged bullet"""
        y_offset = (BULLET_HEIGHT * [1, CHARGE_LEVEL_1_SIZE, CHARGE_LEVEL_2_SIZE, CHARGE_LEVEL_3_SIZE][self.charge_level]) // 2
        return Bullet(
            self.x + self.width,
            self.y + self.height // 2 - y_offset,
            True,
            self.charge_level
        )

    def take_damage(self):
        """Player takes damage"""
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = PLAYER_INVINCIBILITY_TIME // (1000 // FPS)
            return True
        return False

    def add_speed(self):
        """Power-up: increase speed"""
        self.speed = min(self.speed + 1, 10)

    def add_power(self):
        """Power-up: increase power"""
        self.power_level = min(self.power_level + 1, 5)

    def draw(self, screen):
        # Blink effect when invincible
        if self.invincible and self.blink_timer % 10 < 5:
            return

        # Draw player as a triangle (pointing right)
        points = [
            (self.x + self.width, self.y + self.height // 2),  # Tip
            (self.x, self.y),  # Top left
            (self.x, self.y + self.height)  # Bottom left
        ]
        pygame.draw.polygon(screen, BLUE, points)

        # Draw charge indicator
        if self.charging and self.charge_level > 0:
            # Draw charging glow
            glow_colors = [WHITE, WHITE, YELLOW, RED]
            glow_color = glow_colors[self.charge_level]
            glow_size = 5 + self.charge_level * 3

            pygame.draw.circle(
                screen,
                glow_color,
                (int(self.x + self.width // 2), int(self.y + self.height // 2)),
                glow_size,
                2
            )
