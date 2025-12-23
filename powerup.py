import pygame
from constants import *

class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.powerup_type = powerup_type
        self.size = POWERUP_SIZE
        self.speed = POWERUP_SPEED
        self.active = True

        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        # Set color based on type
        if powerup_type == POWERUP_TYPE_FORCE:
            self.color = ORANGE
            self.name = "FORCE"
        elif powerup_type == POWERUP_TYPE_SPEED:
            self.color = GREEN
            self.name = "SPEED"
        else:  # POWERUP_TYPE_POWER
            self.color = RED
            self.name = "POWER"

    def update(self):
        if not self.active:
            return

        # Move slowly to the left
        self.x -= self.speed

        self.rect.x = self.x
        self.rect.y = self.y

        # Deactivate if off screen
        if self.x < -self.size:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return

        # Draw as hexagon
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        radius = self.size // 2

        # Calculate hexagon points
        points = []
        for i in range(6):
            angle = i * 60 * (3.14159 / 180)
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append((px, py))

        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)

        # Draw letter indicator
        font = pygame.font.Font(None, 16)
        letter = self.name[0]  # F, S, or P
        text = font.render(letter, True, WHITE)
        text_rect = text.get_rect(center=(center_x, center_y))
        screen.blit(text, text_rect)

import math
