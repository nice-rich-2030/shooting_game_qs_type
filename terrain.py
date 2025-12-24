import pygame
from constants import *

class TerrainSegment:
    def __init__(self, x, top_height, bottom_height, width=100):
        """
        地形セグメント - 画面を右から左へスクロールする障害物

        Args:
            x: 開始X座標（通常は画面右端 = SCREEN_WIDTH）
            top_height: 天井の高さ（画面上端からの距離、ピクセル）
            bottom_height: 床の高さ（画面下端からの距離、ピクセル）
            width: セグメントの幅（ピクセル）
        """
        self.x = x
        self.top_height = top_height
        self.bottom_height = bottom_height
        self.width = width
        self.active = True
        self.scroll_speed = TERRAIN_SCROLL_SPEED

        # 衝突判定用のRect（上下2つ）
        self.top_rect = pygame.Rect(x, 0, width, top_height)
        self.bottom_rect = pygame.Rect(
            x,
            SCREEN_HEIGHT - bottom_height,
            width,
            bottom_height
        )

    def update(self):
        """地形を左にスクロールさせる"""
        # 左にスクロール
        self.x -= self.scroll_speed

        # Rect更新
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

        # 画面外に出たら非アクティブ化
        if self.x + self.width < 0:
            self.active = False

    def draw(self, screen):
        """地形を描画"""
        # 天井部分（上からtop_heightまで）
        pygame.draw.rect(screen, TERRAIN_COLOR, self.top_rect)
        pygame.draw.rect(screen, TERRAIN_EDGE_COLOR, self.top_rect, 2)  # 枠線

        # 床部分（下からbottom_heightまで）
        pygame.draw.rect(screen, TERRAIN_COLOR, self.bottom_rect)
        pygame.draw.rect(screen, TERRAIN_EDGE_COLOR, self.bottom_rect, 2)

        # ディテール（配管、パネル、警告線など）
        self._draw_details(screen)

    def _draw_details(self, screen):
        """地形のディテールを描画（配管、パネル、警告線）"""
        # 1. 警告ストライプ（天井の下端）
        if self.top_height > 5:
            stripe_y = self.top_height - 5
            for i in range(0, self.width, 20):
                color = YELLOW if (i // 20) % 2 == 0 else BLACK
                pygame.draw.rect(screen, color,
                               (self.x + i, stripe_y, 10, 5))

        # 2. 配管（天井）
        if self.top_height > 20:
            pipe_y = self.top_height - 15
            pygame.draw.line(screen, DARK_GRAY,
                           (self.x, pipe_y),
                           (self.x + self.width, pipe_y), 4)
            # 配管のジョイント
            for i in range(0, self.width, 40):
                pygame.draw.circle(screen, LIGHT_GRAY,
                                 (self.x + i, pipe_y), 5)

        # 3. パネル（床）
        if self.bottom_height > 20:
            panel_start_y = SCREEN_HEIGHT - self.bottom_height + 10
            for i in range(0, self.width, 30):
                pygame.draw.line(screen, DARK_GRAY,
                               (self.x + i, panel_start_y),
                               (self.x + i, SCREEN_HEIGHT), 1)

        # 4. 警告ストライプ（床の上端）
        if self.bottom_height > 5:
            stripe_y = SCREEN_HEIGHT - self.bottom_height
            for i in range(0, self.width, 20):
                color = YELLOW if (i // 20) % 2 == 0 else BLACK
                pygame.draw.rect(screen, color,
                               (self.x + i, stripe_y, 10, 5))

    def collides_with(self, rect):
        """
        指定されたRectと衝突しているか判定

        Args:
            rect: 判定対象のpygame.Rect

        Returns:
            bool: 衝突している場合True
        """
        return (self.top_rect.colliderect(rect) or
                self.bottom_rect.colliderect(rect))
