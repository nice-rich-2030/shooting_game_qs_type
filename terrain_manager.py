import random
from constants import *
from terrain import TerrainSegment

class TerrainManager:
    def __init__(self):
        """地形生成・管理クラス"""
        self.segments = []
        self.spawn_timer = 0
        self.spawn_interval = TERRAIN_SPAWN_INTERVAL
        self.segment_width = TERRAIN_SEGMENT_WIDTH

        # 現在の地形パターン
        self.current_pattern = 0  # 0=Open, 1=NarrowTop, 2=NarrowBottom, 3=NarrowMiddle, 4=Wavy
        self.pattern_timer = 0
        self.pattern_duration = PATTERN_DURATION_EASY

        # Wave進行（game.pyから設定される）
        self.current_wave = 1

        # 新しく生成された砲台を一時保存
        self.new_turrets = []

    def update(self):
        """地形システムの更新"""
        # 既存セグメントの更新
        for segment in self.segments:
            segment.update()

        # 非アクティブなセグメントを削除
        self.segments = [s for s in self.segments if s.active]

        # 新しいセグメント生成
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_segment()

        # パターン切り替え
        self.pattern_timer += 1
        if self.pattern_timer >= self.pattern_duration:
            self.pattern_timer = 0
            self._next_pattern()

    def spawn_segment(self):
        """現在のパターンに基づいて新しいセグメントを生成"""
        # Wave 1は常にOpenパターン
        if self.current_wave == 1:
            pattern_index = 0
        else:
            pattern_index = self.current_pattern

        patterns = [
            self._pattern_open,          # 0
            self._pattern_narrow_top,    # 1
            self._pattern_narrow_bottom, # 2
            self._pattern_narrow_middle, # 3
            self._pattern_wavy          # 4
        ]

        top_h, bottom_h = patterns[pattern_index]()
        segment = TerrainSegment(SCREEN_WIDTH, top_h, bottom_h, self.segment_width)
        self.segments.append(segment)

        # Wave 2以降、確率で砲台を配置
        if self.current_wave >= 2:
            spawn_chances = [0, 0, TURRET_SPAWN_CHANCE_WAVE_2, TURRET_SPAWN_CHANCE_WAVE_3, TURRET_SPAWN_CHANCE_WAVE_4]
            spawn_chance = spawn_chances[min(self.current_wave, 4)]

            if random.random() < spawn_chance:
                turret = self._spawn_turret_on_segment(segment)
                if turret:
                    self.new_turrets.append(turret)

    def _next_pattern(self):
        """次のパターンへ切り替え（Wave別）"""
        if self.current_wave == 1:
            # Wave 1: Openパターンのみ
            self.current_pattern = 0
        elif self.current_wave == 2:
            # Wave 2: Open(30%), NarrowTop(35%), NarrowBottom(35%)
            rand = random.random()
            if rand < 0.3:
                self.current_pattern = 0  # Open
            elif rand < 0.65:
                self.current_pattern = 1  # NarrowTop
            else:
                self.current_pattern = 2  # NarrowBottom
        elif self.current_wave == 3:
            # Wave 3: NarrowTop(25%), NarrowBottom(25%), Wavy(50%)
            rand = random.random()
            if rand < 0.25:
                self.current_pattern = 1  # NarrowTop
            elif rand < 0.5:
                self.current_pattern = 2  # NarrowBottom
            else:
                self.current_pattern = 4  # Wavy
        else:
            # Wave 4以降: すべて均等（各20%）
            self.current_pattern = random.randint(0, 4)

    def set_wave(self, wave):
        """
        現在のWaveを設定（game.pyから呼ばれる）

        Args:
            wave: 現在のWave番号（1-4）
        """
        self.current_wave = wave

        # Wave別のパターン持続時間を設定
        if wave == 1:
            self.pattern_duration = 9999  # Wave 1は永続（実質パターン変更なし）
        elif wave == 2:
            self.pattern_duration = PATTERN_DURATION_EASY  # 10秒
        elif wave == 3:
            self.pattern_duration = PATTERN_DURATION_NORMAL  # 8秒
        else:
            self.pattern_duration = PATTERN_DURATION_HARD  # 6秒

    # === 地形パターン定義 ===

    def _pattern_open(self):
        """パターン0: 開けた空間 - 初心者向け"""
        top = random.randint(0, 50)
        bottom = random.randint(0, 50)
        return top, bottom

    def _pattern_narrow_top(self):
        """パターン1: 上部が狭い"""
        top = random.randint(100, 200)
        bottom = random.randint(0, 50)
        return top, bottom

    def _pattern_narrow_bottom(self):
        """パターン2: 下部が狭い"""
        top = random.randint(0, 50)
        bottom = random.randint(100, 200)
        return top, bottom

    def _pattern_narrow_middle(self):
        """パターン3: 上下両方が狭い - 難易度高"""
        top = random.randint(120, 180)
        bottom = random.randint(120, 180)

        # 最低限の通路幅を確保（150ピクセル）
        if top + bottom > SCREEN_HEIGHT - 150:
            top = min(top, 150)
            bottom = SCREEN_HEIGHT - 150 - top

        return top, bottom

    def _pattern_wavy(self):
        """パターン4: 波型の変化"""
        # 前のセグメントから滑らかに変化
        if self.segments:
            prev = self.segments[-1]
            top = prev.top_height + random.randint(-20, 20)
            bottom = prev.bottom_height + random.randint(-20, 20)
            top = max(0, min(top, 200))
            bottom = max(0, min(bottom, 200))
        else:
            top = random.randint(50, 100)
            bottom = random.randint(50, 100)

        return top, bottom

    def draw(self, screen):
        """すべての地形セグメントを描画"""
        for segment in self.segments:
            segment.draw(screen)

    def check_collision(self, rect):
        """
        指定されたRectが地形と衝突しているか判定

        Args:
            rect: 判定対象のpygame.Rect

        Returns:
            bool: 衝突している場合True
        """
        for segment in self.segments:
            if segment.collides_with(rect):
                return True
        return False

    def get_safe_spawn_y(self):
        """
        敵の安全な出現Y座標を取得（地形と重ならない位置）

        Returns:
            int: 安全なY座標
        """
        # 現在の画面右端の地形情報を取得（最後のセグメントを参照）
        if self.segments:
            last_seg = self.segments[-1]
            top_limit = last_seg.top_height + 50  # 天井から50px下
            bottom_limit = SCREEN_HEIGHT - last_seg.bottom_height - 50  # 床から50px上

            # この範囲内でランダムなY座標
            if top_limit < bottom_limit:
                return random.randint(int(top_limit), int(bottom_limit))

        # デフォルト（地形がない場合、または範囲が無効な場合）
        return random.randint(100, SCREEN_HEIGHT - 100)

    def _spawn_turret_on_segment(self, segment):
        """
        セグメントに砲台を配置

        Args:
            segment: 地形セグメント

        Returns:
            Enemy or None: 生成された砲台敵
        """
        from enemy import Enemy

        # 天井または床にランダム配置（十分な高さがある方を選択）
        can_spawn_ceiling = segment.top_height > 80  # TURRET_SIZE + margin
        can_spawn_floor = segment.bottom_height > 80  # TURRET_SIZE + margin

        if not can_spawn_ceiling and not can_spawn_floor:
            return None  # 地形が薄すぎて配置できない

        # 両方配置可能な場合はランダム、片方のみの場合はそちらを選択
        if can_spawn_ceiling and can_spawn_floor:
            spawn_on_ceiling = random.random() < 0.5
        else:
            spawn_on_ceiling = can_spawn_ceiling

        # 砲台の位置を計算
        turret_x = segment.x + segment.width // 2

        if spawn_on_ceiling:
            # 天井砲台
            turret_y = segment.top_height - TURRET_SIZE
            position = 'ceiling'
        else:
            # 床砲台
            turret_y = SCREEN_HEIGHT - segment.bottom_height
            position = 'floor'

        # 砲台敵を生成
        turret = Enemy(turret_x, turret_y, ENEMY_TYPE_TURRET)
        turret.turret_position = position

        # Wave別の射撃間隔を設定
        if self.current_wave == 2:
            turret.shoot_interval = TURRET_INTERVAL_WAVE_2
        elif self.current_wave == 3:
            turret.shoot_interval = TURRET_INTERVAL_WAVE_3
        else:  # Wave 4以降
            turret.shoot_interval = TURRET_INTERVAL_WAVE_4

        turret.shoot_cooldown = turret.shoot_interval

        return turret

    def get_new_turrets(self):
        """
        新しく生成された砲台のリストを取得してクリア

        Returns:
            list: 新しく生成された砲台のリスト
        """
        turrets = self.new_turrets.copy()
        self.new_turrets.clear()
        return turrets
