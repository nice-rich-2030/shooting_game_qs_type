import pygame
import math
from constants import *

class Bullet:
    def __init__(self, x, y, is_player_bullet=True, charge_level=0, velocity_x=None, velocity_y=None):
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

        # 速度ベクトル設定（velocity_x/yが指定されている場合は斜め弾）
        if velocity_x is not None and velocity_y is not None:
            self.velocity_x = velocity_x
            self.velocity_y = velocity_y
            # 斜め弾は色を変える（敵弾の場合のみ）
            if not is_player_bullet:
                self.color = RED  # 狙い撃ち弾は赤色
        else:
            # 通常の直線弾（後方互換性）
            if is_player_bullet:
                self.velocity_x = self.speed
                self.velocity_y = 0
            else:
                self.velocity_x = self.speed
                self.velocity_y = 0

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        if not self.active:
            return

        # 速度ベクトルで移動（斜め弾対応）
        self.x += self.velocity_x
        self.y += self.velocity_y

        self.rect.x = self.x
        self.rect.y = self.y

        # 画面外判定（X方向とY方向）
        if (self.x > SCREEN_WIDTH + 50 or self.x < -50 or
            self.y > SCREEN_HEIGHT + 50 or self.y < -50):
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


def create_aimed_bullet(start_x, start_y, target_x, target_y, speed, is_player=False):
    """
    プレイヤーを狙う弾丸を作成

    Args:
        start_x, start_y: 発射位置
        target_x, target_y: 目標位置（プレイヤー）
        speed: 弾速
        is_player: プレイヤーの弾か

    Returns:
        Bullet: 狙い撃ち弾
    """
    # ベクトル計算
    dx = target_x - start_x
    dy = target_y - start_y
    distance = math.sqrt(dx**2 + dy**2)

    # ゼロ除算回避
    if distance == 0:
        distance = 1

    # 正規化して速度を掛ける
    velocity_x = (dx / distance) * speed
    velocity_y = (dy / distance) * speed

    return Bullet(start_x, start_y, is_player, 0, velocity_x, velocity_y)
