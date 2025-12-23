import pygame
from constants import *
from bullet import Bullet

class Force:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = FORCE_SIZE
        self.state = FORCE_DETACHED  # Start detached (player doesn't have it initially)
        self.active = False  # Force needs to be acquired first

        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        # Shooting
        self.shoot_cooldown = 0
        self.shoot_delay = 10

    def activate(self, x, y):
        """Activate the force (from powerup)"""
        self.active = True
        self.x = x
        self.y = y
        self.state = FORCE_ATTACHED_FRONT
        self.rect.x = self.x
        self.rect.y = self.y

    def toggle_state(self):
        """Toggle between attached front, attached back, and detached"""
        if not self.active:
            return

        if self.state == FORCE_ATTACHED_FRONT:
            self.state = FORCE_ATTACHED_BACK
        elif self.state == FORCE_ATTACHED_BACK:
            self.state = FORCE_DETACHED
        else:
            self.state = FORCE_ATTACHED_FRONT

    def update(self, player_x, player_y, player_width, player_height):
        if not self.active:
            return

        # Update position based on state
        if self.state == FORCE_ATTACHED_FRONT:
            # Attach to front of player
            self.x = player_x + player_width + FORCE_ATTACH_DISTANCE - self.size // 2
            self.y = player_y + player_height // 2 - self.size // 2

        elif self.state == FORCE_ATTACHED_BACK:
            # Attach to back of player
            self.x = player_x - FORCE_ATTACH_DISTANCE - self.size // 2
            self.y = player_y + player_height // 2 - self.size // 2

        elif self.state == FORCE_DETACHED:
            # Move slowly forward when detached
            self.x += FORCE_DETACHED_SPEED

            # Keep on screen
            if self.x > SCREEN_WIDTH - self.size:
                self.x = SCREEN_WIDTH - self.size
            if self.x < 0:
                self.x = 0
            if self.y > SCREEN_HEIGHT - self.size:
                self.y = SCREEN_HEIGHT - self.size
            if self.y < 0:
                self.y = 0

        self.rect.x = self.x
        self.rect.y = self.y

        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self):
        """Force shoots bullets (synchronized with player)"""
        if not self.active:
            return []

        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_delay

            # Shoot from the front of the force
            bullet_x = self.x + self.size
            bullet_y = self.y + self.size // 2 - 2
            return [Bullet(bullet_x, bullet_y, True, 0)]

        return []

    def can_absorb_bullets(self):
        """Check if force can absorb enemy bullets (when active)"""
        return self.active

    def draw(self, screen):
        if not self.active:
            return

        # Draw main orange circle
        center_x = int(self.x + self.size // 2)
        center_y = int(self.y + self.size // 2)
        radius = self.size // 2

        pygame.draw.circle(screen, ORANGE, (center_x, center_y), radius)

        # Draw inner glow
        inner_radius = radius - 5
        if inner_radius > 0:
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), inner_radius)

        # Draw core
        core_radius = radius - 10
        if core_radius > 0:
            pygame.draw.circle(screen, WHITE, (center_x, center_y), core_radius)

        # Draw state indicator
        if self.state == FORCE_ATTACHED_FRONT:
            # Draw arrow pointing right
            pygame.draw.line(screen, WHITE, (center_x - 5, center_y), (center_x + 5, center_y), 2)
            pygame.draw.line(screen, WHITE, (center_x + 5, center_y), (center_x, center_y - 5), 2)
            pygame.draw.line(screen, WHITE, (center_x + 5, center_y), (center_x, center_y + 5), 2)
        elif self.state == FORCE_ATTACHED_BACK:
            # Draw arrow pointing left
            pygame.draw.line(screen, WHITE, (center_x - 5, center_y), (center_x + 5, center_y), 2)
            pygame.draw.line(screen, WHITE, (center_x - 5, center_y), (center_x, center_y - 5), 2)
            pygame.draw.line(screen, WHITE, (center_x - 5, center_y), (center_x, center_y + 5), 2)
