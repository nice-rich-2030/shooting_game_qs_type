import pygame
import random
import math
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
        self.weapon_type = WEAPON_TYPE_NORMAL  # 射撃タイプ

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Shooting
        self.shoot_cooldown = 0
        self.shoot_delay = 10  # frames between shots

        # Charge shot
        self.charging = False
        self.charge_time = 0
        self.charge_level = 0
        self.was_charging = False  # Track charge state for sound triggers

        # Invincibility
        self.invincible = False
        self.invincible_timer = 0
        self.blink_timer = 0

        # Sound manager (set by game.py)
        self.sound_manager = None

        # Animation state variables
        self.engine_timer = 0           # エンジン炎用タイマー
        self.tilt_angle = 0.0           # 傾き角度（-1.0 ~ 1.0）
        self.recoil_offset = 0.0        # 射撃反動オフセット
        self.idle_timer = 0             # アイドルホバリングタイマー
        self.shake_timer = 0            # 被弾シェイクタイマー
        self.shake_intensity = 3        # シェイク強度

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

        # === Animation Updates ===

        # 1. 傾きアニメーションの更新
        if keys[pygame.K_UP]:
            self.tilt_angle = max(-1.0, self.tilt_angle - 0.15)
        elif keys[pygame.K_DOWN]:
            self.tilt_angle = min(1.0, self.tilt_angle + 0.15)
        else:
            self.tilt_angle *= 0.9  # 復元

        # 2. アイドルタイマーの更新
        if not any([keys[pygame.K_UP], keys[pygame.K_DOWN],
                    keys[pygame.K_LEFT], keys[pygame.K_RIGHT]]):
            self.idle_timer += 1
        else:
            self.idle_timer = 0

        # 3. 反動の復元
        if self.recoil_offset < 0:
            self.recoil_offset += 0.5
        elif self.recoil_offset > 0:
            self.recoil_offset = 0

        # 4. シェイクタイマーの更新
        if self.shake_timer > 0:
            self.shake_timer -= 1

        # 5. エンジンタイマー
        self.engine_timer += 1

        # Charge shot logic
        if keys[pygame.K_x]:
            # Detect charge start
            if not self.was_charging and self.sound_manager:
                self.sound_manager.play_charge_start()

            self.was_charging = True
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

            # Play charge loop sound
            if self.sound_manager and self.charge_level > 0:
                self.sound_manager.play_charge_loop(self.charge_level)
        else:
            # Release charge shot
            if self.charging and self.charge_level > 0:
                if self.sound_manager:
                    self.sound_manager.play_charge_release(self.charge_level)
                    self.sound_manager.stop_charge_loop()

                bullets = [self.create_charge_bullet()]
                self.charge_time = 0
                self.charge_level = 0
                self.charging = False
                self.was_charging = False
                return bullets

            self.charging = False
            self.charge_time = 0
            self.charge_level = 0
            self.was_charging = False

        return []

    def shoot(self):
        """Shoot normal bullets (Z key)"""
        if self.shoot_cooldown <= 0:
            # 武器タイプに応じてクールダウンを設定
            if self.weapon_type == WEAPON_TYPE_3WAY:
                self.shoot_cooldown = WEAPON_3WAY_DELAY  # 30 frames
            else:
                self.shoot_cooldown = WEAPON_NORMAL_DELAY  # 10 frames

            self.recoil_offset = -3  # 反動追加
            if self.sound_manager:
                self.sound_manager.play_player_shoot()

            bullets = []
            base_x = self.x + self.width
            base_y = self.y + self.height // 2

            if self.weapon_type == WEAPON_TYPE_NORMAL:
                # 通常の水平射撃
                bullets.append(Bullet(base_x, base_y - 2, True, 0))

            elif self.weapon_type == WEAPON_TYPE_3WAY:
                # 3方向射撃
                # 1. 中央（水平）
                bullets.append(Bullet(base_x, base_y - 2, True, 0))

                # 2. 上40度
                angle_up = math.radians(WAY3_ANGLE_DEG)
                vx_up = BULLET_SPEED * math.cos(angle_up)
                vy_up = -BULLET_SPEED * math.sin(angle_up)  # 上方向は負
                bullets.append(Bullet(base_x, base_y - 2, True, 0, vx_up, vy_up))

                # 3. 下40度
                angle_down = math.radians(-WAY3_ANGLE_DEG)
                vx_down = BULLET_SPEED * math.cos(angle_down)
                vy_down = -BULLET_SPEED * math.sin(angle_down)  # 下方向は正
                bullets.append(Bullet(base_x, base_y - 2, True, 0, vx_down, vy_down))

            return bullets
        return []

    def create_charge_bullet(self):
        """Create a charged bullet"""
        # 反動を追加
        self.recoil_offset = -5 * self.charge_level

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
            self.shake_timer = 10  # シェイク追加
            return True
        return False

    def add_speed(self):
        """Power-up: increase speed"""
        self.speed = min(self.speed + 1, 10)

    def add_power(self):
        """Power-up: increase power"""
        self.power_level = min(self.power_level + 1, 5)

    def toggle_weapon(self):
        """武器タイプを切り替え（Vキーで呼ばれる）"""
        if self.weapon_type == WEAPON_TYPE_NORMAL:
            self.weapon_type = WEAPON_TYPE_3WAY
        else:
            self.weapon_type = WEAPON_TYPE_NORMAL

    def set_weapon_type(self, weapon_type):
        """武器タイプを設定"""
        self.weapon_type = weapon_type

    def draw(self, screen):
        # Blink effect when invincible
        if self.invincible and self.blink_timer % 10 < 5:
            return

        # === アニメーションオフセットの計算 ===

        # 1. 射撃反動オフセット
        recoil_x = int(self.recoil_offset)

        # 2. 傾きオフセット
        tilt_y = int(self.tilt_angle * 5)

        # 3. アイドルホバリング
        idle_y = 0
        if self.idle_timer > 0:
            idle_y = int(math.sin(self.idle_timer * 0.05) * 2)

        # 4. 被弾シェイク
        shake_x = 0
        shake_y = 0
        if self.shake_timer > 0:
            shake_x = random.randint(-self.shake_intensity, self.shake_intensity)
            shake_y = random.randint(-self.shake_intensity, self.shake_intensity)

        # 5. チャージ脈動
        pulse_scale = 1.0
        if self.charging and self.charge_level > 0:
            pulse_scale = 1.0 + math.sin(self.charge_time * 0.2) * 0.1 * self.charge_level

        # === 総合オフセット ===
        total_offset_x = self.x + recoil_x + shake_x
        total_offset_y = self.y + tilt_y + idle_y + shake_y

        # === プレイヤー三角形の描画 ===
        center_x = total_offset_x + self.width // 2
        center_y = total_offset_y + self.height // 2

        # 脈動を適用したサイズ
        scaled_width = int(self.width * pulse_scale)
        scaled_height = int(self.height * pulse_scale)

        # 三角形の頂点（脈動適用）
        points = [
            (center_x + scaled_width // 2, center_y),  # 先端（右）
            (center_x - scaled_width // 2, center_y - scaled_height // 2),  # 左上
            (center_x - scaled_width // 2, center_y + scaled_height // 2)   # 左下
        ]
        pygame.draw.polygon(screen, BLUE, points)

        # === エンジン噴射エフェクト ===
        # 三角形の左側（後方）から炎を描画
        flame_base_x = center_x - scaled_width // 2
        flame_y1 = center_y - scaled_height // 4  # 上の炎
        flame_y2 = center_y + scaled_height // 4  # 下の炎

        # フレームごとにランダムな長さ
        flame_length = 5 + random.randint(0, 5)

        # 2本の炎を描画
        pygame.draw.line(screen, ORANGE,
                         (flame_base_x, flame_y1),
                         (flame_base_x - flame_length, flame_y1), 3)
        pygame.draw.line(screen, YELLOW,
                         (flame_base_x, flame_y2),
                         (flame_base_x - flame_length + 2, flame_y2), 2)

        # === チャージインジケーター（既存） ===
        if self.charging and self.charge_level > 0:
            glow_colors = [WHITE, WHITE, YELLOW, RED]
            glow_color = glow_colors[self.charge_level]
            glow_size = 5 + self.charge_level * 3

            pygame.draw.circle(
                screen,
                glow_color,
                (int(center_x), int(center_y)),
                glow_size,
                2
            )
