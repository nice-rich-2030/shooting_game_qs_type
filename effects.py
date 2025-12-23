import pygame
import random
import math
from constants import *

class Explosion:
    def __init__(self, x, y, size=30):
        self.x = x
        self.y = y
        self.size = size
        self.timer = EXPLOSION_DURATION
        self.active = True

        # Create particles
        self.particles = []
        for i in range(EXPLOSION_PARTICLE_COUNT):
            angle = (360 / EXPLOSION_PARTICLE_COUNT) * i
            speed = random.uniform(2, 5)
            particle = {
                'x': x,
                'y': y,
                'vx': math.cos(math.radians(angle)) * speed,
                'vy': math.sin(math.radians(angle)) * speed,
                'size': random.randint(3, 8),
                'color': random.choice([RED, ORANGE, YELLOW, WHITE])
            }
            self.particles.append(particle)

    def update(self):
        if not self.active:
            return

        self.timer -= 1
        if self.timer <= 0:
            self.active = False
            return

        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['size'] = max(1, particle['size'] - 0.3)

    def draw(self, screen):
        if not self.active:
            return

        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(
                screen,
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                int(particle['size'])
            )

        # Draw main explosion flash
        alpha = self.timer / EXPLOSION_DURATION
        flash_size = int(self.size * alpha)
        if flash_size > 0:
            colors = [YELLOW, ORANGE, RED]
            color_index = min(2, int((1 - alpha) * 3))
            pygame.draw.circle(
                screen,
                colors[color_index],
                (int(self.x), int(self.y)),
                flash_size,
                3
            )
