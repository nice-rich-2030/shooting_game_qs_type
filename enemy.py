import pygame
import math
import random
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

        elif enemy_type == ENEMY_TYPE_TANK:
            self.hp = ENEMY_TANK_HP
            self.speed = ENEMY_TANK_SPEED
            self.score = ENEMY_TANK_SCORE
            self.color = ORANGE
            self.size = 40
            self.shoot_interval = 90  # Shoots every 1.5 seconds

        elif enemy_type == ENEMY_TYPE_TURRET:
            self.hp = ENEMY_TURRET_HP
            self.speed = ENEMY_TURRET_SPEED  # 0
            self.score = ENEMY_TURRET_SCORE
            self.color = PURPLE
            self.size = TURRET_SIZE
            self.shoot_interval = ENEMY_TURRET_SHOOT_INTERVAL

            # 砲台特有のプロパティ
            self.is_turret = True
            self.turret_position = 'ceiling'  # または 'floor'（後で設定）

        elif enemy_type == ENEMY_TYPE_BOSS_1:
            self.hp = BOSS_1_HP
            self.speed = BOSS_1_SPEED
            self.score = BOSS_1_SCORE
            self.color = RED
            self.size = BOSS_1_SIZE
            self.shoot_interval = BOSS_1_SHOOT_INTERVAL
            self.is_boss = True

        elif enemy_type == ENEMY_TYPE_BOSS_2:
            self.hp = BOSS_2_HP
            self.speed = BOSS_2_SPEED
            self.score = BOSS_2_SCORE
            self.color = YELLOW
            self.size = BOSS_2_SIZE
            self.shoot_interval = BOSS_2_SHOOT_INTERVAL
            self.is_boss = True

        else:  # ENEMY_TYPE_BOSS_3
            self.hp = BOSS_3_HP
            self.speed = BOSS_3_SPEED
            self.score = BOSS_3_SCORE
            self.color = PURPLE
            self.size = BOSS_3_SIZE
            self.shoot_interval = BOSS_3_SHOOT_INTERVAL
            self.is_boss = True

        self.max_hp = self.hp
        self.shoot_cooldown = self.shoot_interval
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        # For wave movement
        self.initial_y = y
        self.wave_amplitude = 50
        self.wave_frequency = 0.05

        # For charge movement
        self.target_y = None

    def update(self, player_y, player_x=None):
        if not self.active:
            return []

        self.time_alive += 1
        bullets = []

        # Movement based on type
        if self.enemy_type == ENEMY_TYPE_TURRET:
            # 砲台は地形と一緒にスクロール
            self.x -= TERRAIN_SCROLL_SPEED

        elif self.enemy_type == ENEMY_TYPE_STRAIGHT:
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

        elif self.enemy_type == ENEMY_TYPE_TANK:
            # Slow movement
            self.x -= self.speed

        elif self.enemy_type == ENEMY_TYPE_BOSS_1:
            # Boss 1: Simple vertical oscillation
            # Stay at x=600 (right side but visible)
            if self.x > 600:
                self.x -= self.speed
            # Vertical sine wave
            self.y = SCREEN_HEIGHT // 2 + math.sin(self.time_alive * 0.02) * 100

        elif self.enemy_type == ENEMY_TYPE_BOSS_2:
            # Boss 2: Figure-8 pattern
            if self.x > 600:
                self.x -= self.speed
            else:
                # Figure-8 movement (after reaching position)
                self.y = SCREEN_HEIGHT // 2 + math.sin(self.time_alive * 0.03) * 80
                self.x = 600 + math.cos(self.time_alive * 0.015) * 50

        else:  # ENEMY_TYPE_BOSS_3
            # Boss 3: More complex circular pattern
            if self.x > 600:
                self.x -= self.speed * 0.5
            else:
                # Circular pattern (after reaching position)
                angle = self.time_alive * 0.04
                self.y = SCREEN_HEIGHT // 2 + math.sin(angle) * 120
                self.x = 600 + math.cos(angle) * 80

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
                # 砲台、WAVE型、ボスの場合はプレイヤー座標を渡す
                if self.enemy_type in [ENEMY_TYPE_TURRET, ENEMY_TYPE_WAVE, ENEMY_TYPE_BOSS_1, ENEMY_TYPE_BOSS_2, ENEMY_TYPE_BOSS_3] and player_x is not None:
                    bullets = self.shoot(player_x, player_y)
                else:
                    bullets = self.shoot()

        return bullets

    def shoot(self, player_x=None, player_y=None):
        """Enemy shoots bullets"""
        bullets = []

        if self.enemy_type == ENEMY_TYPE_WAVE:
            # 30%の確率でプレイヤー狙い撃ち、70%で通常弾
            if player_x is not None and player_y is not None and random.random() < AIMED_BULLET_CHANCE_WAVE:
                from bullet import create_aimed_bullet
                bullet = create_aimed_bullet(
                    self.x,
                    self.y + self.size // 2,
                    player_x,
                    player_y,
                    ENEMY_BULLET_SPEED_WAVE,  # 速度3に変更
                    False
                )
            else:
                # 通常の左方向弾（速度を明示的に指定）
                bullet = Bullet(
                    self.x,
                    self.y + self.size // 2,
                    False,
                    0,
                    -ENEMY_BULLET_SPEED_WAVE,  # 速度3に変更
                    0
                )
            bullets.append(bullet)

        elif self.enemy_type == ENEMY_TYPE_TANK:
            # 3方向拡散弾（左上、左、左下）
            base_speed = ENEMY_BULLET_SPEED_TANK  # 速度4に変更
            angles = [-20, 0, 20]  # 度

            for angle_deg in angles:
                angle_rad = math.radians(angle_deg)
                vx = -base_speed * math.cos(angle_rad)  # 左方向がベース
                vy = -base_speed * math.sin(angle_rad)

                bullet = Bullet(
                    self.x,
                    self.y + self.size // 2,
                    False,
                    0,
                    vx,
                    vy
                )
                bullets.append(bullet)

        elif self.enemy_type == ENEMY_TYPE_TURRET:
            # プレイヤー狙い撃ち弾
            if player_x is not None and player_y is not None:
                from bullet import create_aimed_bullet
                bullet = create_aimed_bullet(
                    self.x + self.size // 2,
                    self.y + self.size // 2,
                    player_x,
                    player_y,
                    ENEMY_BULLET_SPEED_TURRET,  # 速度5に変更
                    False
                )
                bullets.append(bullet)

        elif self.enemy_type == ENEMY_TYPE_BOSS_1:
            # Boss 1: 3-way spread shot
            angles = [-20, 0, 20]
            for angle_deg in angles:
                angle_rad = math.radians(angle_deg)
                vx = -ENEMY_BULLET_SPEED * math.cos(angle_rad)
                vy = -ENEMY_BULLET_SPEED * math.sin(angle_rad)
                bullet = Bullet(
                    self.x,
                    self.y + self.size // 2,
                    False,
                    0,
                    vx,
                    vy
                )
                bullets.append(bullet)

        elif self.enemy_type == ENEMY_TYPE_BOSS_2:
            # Boss 2: Aimed shot + 2 side bullets
            if player_x is not None and player_y is not None:
                from bullet import create_aimed_bullet
                # Aimed bullet at player
                bullet = create_aimed_bullet(
                    self.x,
                    self.y + self.size // 2,
                    player_x,
                    player_y,
                    ENEMY_BULLET_SPEED,
                    False
                )
                bullets.append(bullet)

                # Two side bullets (up and down)
                for angle_deg in [-30, 30]:
                    angle_rad = math.radians(angle_deg)
                    vx = -ENEMY_BULLET_SPEED * math.cos(angle_rad)
                    vy = -ENEMY_BULLET_SPEED * math.sin(angle_rad)
                    bullet = Bullet(
                        self.x,
                        self.y + self.size // 2,
                        False,
                        0,
                        vx,
                        vy
                    )
                    bullets.append(bullet)

        elif self.enemy_type == ENEMY_TYPE_BOSS_3:
            # Boss 3: 5-way radial spread
            if player_x is not None and player_y is not None:
                from bullet import create_aimed_bullet
                # Aimed bullet
                bullet = create_aimed_bullet(
                    self.x,
                    self.y + self.size // 2,
                    player_x,
                    player_y,
                    ENEMY_BULLET_SPEED,
                    False
                )
                bullets.append(bullet)

                # 4 additional bullets in pattern
                for angle_deg in [-40, -20, 20, 40]:
                    angle_rad = math.radians(angle_deg)
                    vx = -ENEMY_BULLET_SPEED * math.cos(angle_rad)
                    vy = -ENEMY_BULLET_SPEED * math.sin(angle_rad)
                    bullet = Bullet(
                        self.x,
                        self.y + self.size // 2,
                        False,
                        0,
                        vx,
                        vy
                    )
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

        elif self.enemy_type == ENEMY_TYPE_TANK:
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

        elif self.enemy_type == ENEMY_TYPE_TURRET:
            # 砲台として描画
            # ベース（台座）
            base_rect = pygame.Rect(self.x, self.y, self.size, self.size)
            pygame.draw.rect(screen, DARK_GRAY, base_rect)
            pygame.draw.rect(screen, self.color, base_rect, 2)

            # 砲身
            barrel_length = 15
            barrel_center_y = self.y + self.size // 2

            pygame.draw.line(
                screen,
                self.color,
                (self.x, barrel_center_y),
                (self.x - barrel_length, barrel_center_y),
                4
            )

            # コア（中心の光）
            core_center = (int(self.x + self.size // 2), int(barrel_center_y))
            pygame.draw.circle(screen, RED, core_center, 5)

        elif self.enemy_type in [ENEMY_TYPE_BOSS_1, ENEMY_TYPE_BOSS_2, ENEMY_TYPE_BOSS_3]:
            # ボスとして描画（大きく目立つ）
            center_x = int(self.x + self.size // 2)
            center_y = int(self.y + self.size // 2)

            # 外側の八角形
            radius = self.size // 2
            octagon_points = []
            for i in range(8):
                angle = math.radians(i * 45 + self.time_alive * 2)
                px = center_x + radius * math.cos(angle)
                py = center_y + radius * math.sin(angle)
                octagon_points.append((px, py))
            pygame.draw.polygon(screen, self.color, octagon_points)
            pygame.draw.polygon(screen, WHITE, octagon_points, 3)

            # 内側の円（コア）
            core_radius = radius // 2
            pygame.draw.circle(screen, RED, (center_x, center_y), core_radius)

            # パルスエフェクト
            pulse = int(10 + abs(math.sin(self.time_alive * 0.1) * 10))
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), pulse, 2)

            # ボスナンバー表示（中央に）
            boss_num = self.enemy_type - ENEMY_TYPE_BOSS_1 + 1
            font = pygame.font.Font(None, 24)
            text = font.render(f"B{boss_num}", True, WHITE)
            text_rect = text.get_rect(center=(center_x, center_y))
            screen.blit(text, text_rect)

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
