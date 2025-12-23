import pygame
import random
from constants import *
from player import Player
from force import Force
from enemy import Enemy
from bullet import Bullet
from powerup import PowerUp
from effects import Explosion
from wave_manager import WaveManager
from sound_manager import SoundManager
from terrain_manager import TerrainManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("R-TYPE Clone")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False

        # Sound manager
        self.sound_manager = SoundManager()

        # Game objects
        self.player = Player()
        self.player.sound_manager = self.sound_manager  # Give player access to sound
        self.force = Force()
        self.enemies = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.powerups = []
        self.explosions = []

        # Wave manager
        self.wave_manager = WaveManager()

        # Terrain manager
        self.terrain_manager = TerrainManager()
        self.terrain_damage_cooldown = 0  # 地形ダメージのクールダウン

        # Score
        self.score = 0

        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Background stars
        self.stars = []
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            speed = random.uniform(0.5, 2)
            self.stars.append({'x': x, 'y': y, 'speed': speed})

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                # Force toggle
                if event.key == pygame.K_c:
                    self.force.toggle_state()
                    self.sound_manager.play_force_toggle()

                # Mute toggle
                if event.key == pygame.K_m:
                    self.sound_manager.toggle_mute()

                # Normal shooting (Z key)
                if event.key == pygame.K_z:
                    new_bullets = self.player.shoot()
                    self.player_bullets.extend(new_bullets)

                    # Force also shoots
                    if self.force.active:
                        force_bullets = self.force.shoot()
                        self.player_bullets.extend(force_bullets)

                # Restart on game over
                if self.game_over and event.key == pygame.K_r:
                    self.__init__()

    def update(self):
        if self.game_over:
            return

        # Get keys for continuous input
        keys = pygame.key.get_pressed()

        # Update player (returns charge bullets if any)
        charge_bullets = self.player.update(keys)
        if charge_bullets:
            self.player_bullets.extend(charge_bullets)
            # Force also shoots when player releases charge
            if self.force.active:
                force_bullets = self.force.shoot()
                self.player_bullets.extend(force_bullets)

        # Continuous shooting when Z is held
        if keys[pygame.K_z]:
            new_bullets = self.player.shoot()
            self.player_bullets.extend(new_bullets)

            if self.force.active:
                force_bullets = self.force.shoot()
                self.player_bullets.extend(force_bullets)

        # Update Force
        self.force.update(self.player.x, self.player.y, self.player.width, self.player.height)

        # Update bullets
        for bullet in self.player_bullets:
            bullet.update()
        self.player_bullets = [b for b in self.player_bullets if b.active]

        for bullet in self.enemy_bullets:
            bullet.update()
        self.enemy_bullets = [b for b in self.enemy_bullets if b.active]

        # Update enemies and spawn new ones
        old_wave = self.wave_manager.current_wave
        self.wave_manager.update()
        if self.wave_manager.current_wave != old_wave:
            self.sound_manager.play_wave_change()
            # Wave変更時に地形マネージャーにも通知
            self.terrain_manager.set_wave(self.wave_manager.current_wave)

        new_enemy = self.wave_manager.spawn_enemy()
        if new_enemy:
            self.enemies.append(new_enemy)

        for enemy in self.enemies:
            new_bullets = enemy.update(self.player.y)
            self.enemy_bullets.extend(new_bullets)
        self.enemies = [e for e in self.enemies if e.active]

        # Update powerups
        for powerup in self.powerups:
            powerup.update()
        self.powerups = [p for p in self.powerups if p.active]

        # Update explosions
        for explosion in self.explosions:
            explosion.update()
        self.explosions = [e for e in self.explosions if e.active]

        # Update terrain
        self.terrain_manager.update()

        # 地形ダメージクールダウン
        if self.terrain_damage_cooldown > 0:
            self.terrain_damage_cooldown -= 1

        # Update stars (scrolling background)
        for star in self.stars:
            star['x'] -= star['speed']
            if star['x'] < 0:
                star['x'] = SCREEN_WIDTH
                star['y'] = random.randint(0, SCREEN_HEIGHT)

        # Collision detection
        self.check_collisions()

        # Check game over
        if self.player.lives <= 0 and not self.game_over:
            self.sound_manager.play_game_over()
            self.game_over = True

    def check_collisions(self):
        # Player bullets vs enemies
        for bullet in self.player_bullets[:]:
            if not bullet.active:
                continue

            for enemy in self.enemies[:]:
                if not enemy.active:
                    continue

                if bullet.rect.colliderect(enemy.rect):
                    bullet.hit()
                    if enemy.take_damage(bullet.damage):
                        # Enemy destroyed
                        self.score += enemy.score
                        self.sound_manager.play_explosion()
                        self.explosions.append(Explosion(
                            enemy.x + enemy.size // 2,
                            enemy.y + enemy.size // 2,
                            enemy.size
                        ))

                        # Chance to drop powerup
                        if random.random() < 0.2:  # 20% chance
                            powerup_type = random.choice([
                                POWERUP_TYPE_FORCE,
                                POWERUP_TYPE_SPEED,
                                POWERUP_TYPE_POWER
                            ])
                            self.powerups.append(PowerUp(
                                enemy.x,
                                enemy.y + enemy.size // 2,
                                powerup_type
                            ))

        # Enemy bullets vs player
        for bullet in self.enemy_bullets[:]:
            if not bullet.active:
                continue

            # Check Force absorption
            if self.force.active and self.force.can_absorb_bullets():
                if bullet.rect.colliderect(self.force.rect):
                    bullet.active = False
                    self.sound_manager.play_force_absorb()
                    continue

            # Check player hit
            if bullet.rect.colliderect(self.player.rect):
                bullet.active = False
                if self.player.take_damage():
                    self.sound_manager.play_player_hit()
                    self.explosions.append(Explosion(
                        self.player.x + self.player.width // 2,
                        self.player.y + self.player.height // 2,
                        30
                    ))

        # Enemy collision with player
        for enemy in self.enemies[:]:
            if not enemy.active:
                continue

            if enemy.rect.colliderect(self.player.rect):
                enemy.active = False
                if self.player.take_damage():
                    self.sound_manager.play_player_hit()
                    self.explosions.append(Explosion(
                        self.player.x + self.player.width // 2,
                        self.player.y + self.player.height // 2,
                        30
                    ))
                self.sound_manager.play_explosion()
                self.explosions.append(Explosion(
                    enemy.x + enemy.size // 2,
                    enemy.y + enemy.size // 2,
                    enemy.size
                ))

        # Powerup collection
        for powerup in self.powerups[:]:
            if not powerup.active:
                continue

            if powerup.rect.colliderect(self.player.rect):
                powerup.active = False
                self.sound_manager.play_powerup()

                if powerup.powerup_type == POWERUP_TYPE_FORCE:
                    if not self.force.active:
                        self.force.activate(self.player.x, self.player.y)
                elif powerup.powerup_type == POWERUP_TYPE_SPEED:
                    self.player.add_speed()
                elif powerup.powerup_type == POWERUP_TYPE_POWER:
                    self.player.add_power()

        # Terrain collision with player
        if self.terrain_damage_cooldown <= 0:
            if self.terrain_manager.check_collision(self.player.rect):
                if self.player.take_damage():
                    self.sound_manager.play_player_hit()
                    self.explosions.append(Explosion(
                        self.player.x + self.player.width // 2,
                        self.player.y + self.player.height // 2,
                        20  # 小さめの爆発
                    ))
                    self.terrain_damage_cooldown = TERRAIN_DAMAGE_COOLDOWN

    def draw(self):
        # Clear screen
        self.screen.fill(BLACK)

        # Draw stars
        for star in self.stars:
            size = int(star['speed'])
            pygame.draw.circle(
                self.screen,
                WHITE,
                (int(star['x']), int(star['y'])),
                max(1, size)
            )

        # Draw terrain (before player but after stars)
        self.terrain_manager.draw(self.screen)

        # Draw game objects
        self.player.draw(self.screen)
        self.force.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.player_bullets:
            bullet.draw(self.screen)

        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)

        for powerup in self.powerups:
            powerup.draw(self.screen)

        for explosion in self.explosions:
            explosion.draw(self.screen)

        # Draw UI
        self.draw_ui()

        # Draw game over screen
        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Lives
        lives_text = self.small_font.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 50))

        # Wave
        wave_text = self.small_font.render(self.wave_manager.get_wave_text(), True, CYAN)
        self.screen.blit(wave_text, (SCREEN_WIDTH - 100, 10))

        # Charge gauge
        if self.player.charging:
            gauge_width = 100
            gauge_height = 10
            gauge_x = self.player.x + self.player.width + 10
            gauge_y = self.player.y

            # Background
            pygame.draw.rect(
                self.screen,
                DARK_GRAY,
                (gauge_x, gauge_y, gauge_width, gauge_height)
            )

            # Charge progress
            charge_progress = min(1.0, self.player.charge_time / CHARGE_LEVEL_3_TIME)
            charge_width = int(gauge_width * charge_progress)

            # Color based on level
            if self.player.charge_level >= 3:
                color = RED
            elif self.player.charge_level >= 2:
                color = YELLOW
            else:
                color = WHITE

            pygame.draw.rect(
                self.screen,
                color,
                (gauge_x, gauge_y, charge_width, gauge_height)
            )

        # Force indicator
        if self.force.active:
            force_text = self.small_font.render("FORCE: Active", True, ORANGE)
            self.screen.blit(force_text, (10, 80))

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)

        # Final score
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        # Restart instruction
        restart_text = self.small_font.render("Press R to Restart or ESC to Quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
