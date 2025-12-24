import random
from constants import *
from enemy import Enemy

class WaveManager:
    def __init__(self):
        self.game_time = 0
        self.spawn_timer = 0
        self.current_wave = 1
        self.enemies_spawned_this_wave = 0
        self.boss_spawned = False  # ボスが既に出現したかのフラグ（Wave 1-3用）
        self.boss_active = False   # ボスがまだ生存しているかのフラグ（Wave 1-3用）

        # Wave 4用の新規プロパティ
        self.last_boss_spawn_time = 0      # 最後にボスを出現させた時刻
        self.active_boss_count = 0          # 現在アクティブなボス数
        self.wave4_start_time = 0           # Wave 4が始まった時刻

    def update(self):
        self.game_time += 1
        self.spawn_timer += 1

        # Update current wave based on time
        if self.game_time < WAVE_1_END:
            new_wave = 1
        elif self.game_time < WAVE_2_END:
            new_wave = 2
        elif self.game_time < WAVE_3_END:
            new_wave = 3
        else:
            new_wave = 4

        # Reset counter when wave changes
        if new_wave != self.current_wave:
            self.current_wave = new_wave
            self.enemies_spawned_this_wave = 0
            self.boss_spawned = False
            self.boss_active = False

            # Wave 4に入った時の初期化
            if new_wave == 4:
                self.wave4_start_time = self.game_time
                self.active_boss_count = 0
                self.last_boss_spawn_time = self.game_time

    def should_spawn_enemy(self):
        """Check if it's time to spawn an enemy"""
        # Vary spawn interval slightly
        spawn_interval = ENEMY_SPAWN_INTERVAL + random.randint(-20, 20)

        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0
            return True
        return False

    def should_spawn_boss_in_wave4(self):
        """Wave 4でボスを出現させるべきかを判定"""
        # Wave 4でない場合は出現しない
        if self.current_wave != 4:
            return False

        # 同時出現制限チェック
        if self.active_boss_count >= WAVE4_MAX_SIMULTANEOUS_BOSSES:
            return False

        # 最低出現間隔チェック
        if self.game_time - self.last_boss_spawn_time < WAVE4_MIN_BOSS_INTERVAL:
            return False

        # Wave 4内での経過時間を計算
        elapsed_in_wave4 = self.game_time - self.wave4_start_time
        elapsed_seconds = elapsed_in_wave4 / 60.0

        # 時間経過に応じた出現確率（5%から25%まで段階的に上昇）
        boss_spawn_chance = min(
            WAVE4_INITIAL_BOSS_CHANCE + (elapsed_seconds / (WAVE4_DIFFICULTY_RAMP_TIME / 60.0)) * (WAVE4_MAX_BOSS_CHANCE - WAVE4_INITIAL_BOSS_CHANCE),
            WAVE4_MAX_BOSS_CHANCE
        )

        # 確率判定
        return random.random() < boss_spawn_chance

    def select_boss_type_for_wave4(self):
        """Wave 4で出現させるボスの種類を選択"""
        elapsed_in_wave4 = self.game_time - self.wave4_start_time
        elapsed_seconds = elapsed_in_wave4 / 60.0

        # 難易度係数 (0.0 ~ 1.0)
        difficulty_factor = min(elapsed_seconds / (WAVE4_DIFFICULTY_RAMP_TIME / 60.0), 1.0)

        # ボス種類の重み計算
        boss_1_weight = max(0.70 - difficulty_factor * 0.55, 0.15)
        boss_2_weight = 0.25 + difficulty_factor * 0.05
        boss_3_weight = 0.05 + difficulty_factor * 0.50

        # 重み付きランダム選択
        rand = random.random()

        if rand < boss_1_weight:
            return ENEMY_TYPE_BOSS_1
        elif rand < boss_1_weight + boss_2_weight:
            return ENEMY_TYPE_BOSS_2
        else:
            return ENEMY_TYPE_BOSS_3

    def spawn_enemy(self):
        """Spawn an enemy based on current wave"""
        enemy_type = None
        x = SCREEN_WIDTH + 50
        y = random.randint(50, SCREEN_HEIGHT - 100)

        # Wave 1: Only straight enemies + boss
        if self.current_wave == 1:
            if self.enemies_spawned_this_wave < 10:
                if self.should_spawn_enemy():
                    enemy_type = ENEMY_TYPE_STRAIGHT
                    self.enemies_spawned_this_wave += 1
            elif not self.boss_spawned:
                # 10体倒した後にボスを出現
                enemy_type = ENEMY_TYPE_BOSS_1
                y = SCREEN_HEIGHT // 2  # ボスは中央に出現
                self.boss_spawned = True
                self.boss_active = True

        # Wave 2: Wave pattern enemies + boss
        elif self.current_wave == 2:
            if self.enemies_spawned_this_wave < 8:
                if self.should_spawn_enemy():
                    enemy_type = ENEMY_TYPE_WAVE
                    self.enemies_spawned_this_wave += 1
            elif not self.boss_spawned:
                # 8体倒した後にボスを出現
                enemy_type = ENEMY_TYPE_BOSS_2
                y = SCREEN_HEIGHT // 2
                self.boss_spawned = True
                self.boss_active = True

        # Wave 3: Charge enemies + some straight + boss
        elif self.current_wave == 3:
            if self.enemies_spawned_this_wave < 10:
                if self.should_spawn_enemy():
                    if random.random() < 0.6:
                        enemy_type = ENEMY_TYPE_CHARGE
                    else:
                        enemy_type = ENEMY_TYPE_STRAIGHT
                    self.enemies_spawned_this_wave += 1
            elif not self.boss_spawned:
                # 10体倒した後にボスを出現
                enemy_type = ENEMY_TYPE_BOSS_3
                y = SCREEN_HEIGHT // 2
                self.boss_spawned = True
                self.boss_active = True

        # Wave 4: All types mixed, infinite + ランダムボス出現
        else:
            # まずボス出現をチェック
            if self.should_spawn_boss_in_wave4():
                # ボスを出現
                enemy_type = self.select_boss_type_for_wave4()
                y = SCREEN_HEIGHT // 2
                self.last_boss_spawn_time = self.game_time
                self.active_boss_count += 1
            elif self.should_spawn_enemy():
                # 通常敵を出現
                rand = random.random()
                if rand < 0.3:
                    enemy_type = ENEMY_TYPE_STRAIGHT
                elif rand < 0.5:
                    enemy_type = ENEMY_TYPE_WAVE
                elif rand < 0.8:
                    enemy_type = ENEMY_TYPE_CHARGE
                else:
                    enemy_type = ENEMY_TYPE_TANK

        if enemy_type is not None:
            return Enemy(x, y, enemy_type)

        return None

    def get_wave_text(self):
        """Get text describing current wave"""
        return f"WAVE {self.current_wave}"

    def on_boss_defeated(self):
        """ボスが撃破された時に呼ばれる"""
        # Wave 1-3のボス撃破処理
        if self.current_wave < 4:
            if self.boss_active:
                self.boss_active = False
                # ボス撃破で次のWaveに強制進行
                if self.current_wave == 1:
                    self.game_time = WAVE_2_START
                elif self.current_wave == 2:
                    self.game_time = WAVE_3_START
                elif self.current_wave == 3:
                    self.game_time = WAVE_4_START
        # Wave 4のボス撃破処理
        else:
            self.active_boss_count = max(0, self.active_boss_count - 1)

    def is_boss_active(self):
        """ボスが生存しているかを返す"""
        return self.boss_active

    def decrease_active_boss_count(self):
        """アクティブなボス数を減らす（Wave 4用、外部から呼ばれる）"""
        self.active_boss_count = max(0, self.active_boss_count - 1)
