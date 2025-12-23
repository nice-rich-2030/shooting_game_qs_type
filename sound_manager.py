import pygame
import numpy as np
from constants import *

class SoundManager:
    """Manages all game sound effects with procedural generation"""

    def __init__(self):
        try:
            # Initialize pygame mixer
            pygame.mixer.init(frequency=SOUND_SAMPLE_RATE, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)  # Allow multiple sounds simultaneously

            self.enabled = SOUND_ENABLED
            self.volume = SOUND_VOLUME_MASTER
            self.muted = False

            # Reserved channel for charge loop
            self.charge_channel = pygame.mixer.Channel(0)

            # Pre-generate all sound effects
            self.sounds = {}
            self._generate_all_sounds()

            print("Sound system initialized successfully")
        except Exception as e:
            print(f"Warning: Sound system initialization failed: {e}")
            self.enabled = False

    def _generate_sine_wave(self, frequency, duration, volume=0.5):
        """Generate a sine wave"""
        samples = int(SOUND_SAMPLE_RATE * duration)
        wave = np.sin(2 * np.pi * frequency * np.arange(samples) / SOUND_SAMPLE_RATE)
        wave = (wave * volume * 32767).astype(np.int16)
        # Stereo
        stereo_wave = np.column_stack((wave, wave))
        return pygame.sndarray.make_sound(stereo_wave)

    def _generate_sweep(self, start_freq, end_freq, duration, volume=0.5):
        """Generate a frequency sweep (rising or falling pitch)"""
        samples = int(SOUND_SAMPLE_RATE * duration)
        freq_range = np.linspace(start_freq, end_freq, samples)
        phase = 2 * np.pi * np.cumsum(freq_range) / SOUND_SAMPLE_RATE
        wave = np.sin(phase)
        wave = (wave * volume * 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        return pygame.sndarray.make_sound(stereo_wave)

    def _generate_noise(self, duration, volume=0.5, decay_time=0.1):
        """Generate noise with exponential decay (explosion-like)"""
        samples = int(SOUND_SAMPLE_RATE * duration)
        noise = np.random.uniform(-1, 1, samples)
        envelope = np.exp(-np.arange(samples) / (SOUND_SAMPLE_RATE * decay_time))
        wave = noise * envelope
        wave = (wave * volume * 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        return pygame.sndarray.make_sound(stereo_wave)

    def _generate_square_wave(self, frequency, duration, volume=0.3):
        """Generate a square wave (8-bit style)"""
        samples = int(SOUND_SAMPLE_RATE * duration)
        wave = np.sign(np.sin(2 * np.pi * frequency * np.arange(samples) / SOUND_SAMPLE_RATE))
        wave = (wave * volume * 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        return pygame.sndarray.make_sound(stereo_wave)

    def _generate_all_sounds(self):
        """Pre-generate all sound effects"""
        # Player shoot
        self.sounds['player_shoot'] = self._generate_sine_wave(600, 0.05, 0.4)

        # Charge shots (3 levels)
        self.sounds['charge_release_1'] = self._generate_sine_wave(400, 0.15, 0.5)
        self.sounds['charge_release_2'] = self._generate_sine_wave(500, 0.15, 0.6)
        self.sounds['charge_release_3'] = self._generate_sine_wave(700, 0.20, 0.7)

        # Charge loops (3 levels) - shorter for looping
        self.sounds['charge_loop_1'] = self._generate_sine_wave(200, 0.3, 0.15)
        self.sounds['charge_loop_2'] = self._generate_sine_wave(250, 0.3, 0.2)
        self.sounds['charge_loop_3'] = self._generate_sine_wave(300, 0.3, 0.25)

        # Charge start
        self.sounds['charge_start'] = self._generate_sine_wave(150, 0.05, 0.3)

        # Force toggle (mechanical click)
        self.sounds['force_toggle'] = self._generate_square_wave(800, 0.03, 0.3)

        # Force absorb (high ping)
        self.sounds['force_absorb'] = self._generate_sine_wave(1200, 0.05, 0.25)

        # Explosion
        self.sounds['explosion'] = self._generate_noise(0.3, 0.5, 0.1)

        # Enemy shoot
        self.sounds['enemy_shoot'] = self._generate_sine_wave(300, 0.04, 0.2)

        # Powerup (rising sweep)
        self.sounds['powerup'] = self._generate_sweep(440, 880, 0.2, 0.5)

        # Player hit (noise + low tone)
        hit_noise = self._generate_noise(0.2, 0.4, 0.08)
        self.sounds['player_hit'] = hit_noise

        # Game over (falling sweep)
        self.sounds['game_over'] = self._generate_sweep(880, 220, 0.5, 0.5)

        # Wave change (two tone alert)
        samples = int(SOUND_SAMPLE_RATE * 0.15)
        wave1 = np.sin(2 * np.pi * 500 * np.arange(samples) / SOUND_SAMPLE_RATE)
        wave2 = np.sin(2 * np.pi * 600 * np.arange(samples) / SOUND_SAMPLE_RATE)
        wave = (wave1 + wave2) / 2
        wave = (wave * 0.4 * 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        self.sounds['wave_change'] = pygame.sndarray.make_sound(stereo_wave)

    def play_player_shoot(self):
        """Play player normal shot sound"""
        if self.enabled and not self.muted:
            self.sounds['player_shoot'].play()

    def play_charge_start(self):
        """Play charge start sound"""
        if self.enabled and not self.muted:
            self.sounds['charge_start'].play()

    def play_charge_loop(self, level):
        """Play continuous charge sound (level 1-3)"""
        if not self.enabled or self.muted:
            return

        level = max(1, min(3, level))  # Clamp to 1-3
        sound_key = f'charge_loop_{level}'

        # Only play if not already playing
        if not self.charge_channel.get_busy():
            self.charge_channel.play(self.sounds[sound_key], loops=-1)  # Loop forever

    def stop_charge_loop(self):
        """Stop the charge loop sound"""
        self.charge_channel.stop()

    def play_charge_release(self, level):
        """Play charge shot release sound (level 1-3)"""
        if not self.enabled or self.muted:
            return

        level = max(1, min(3, level))  # Clamp to 1-3
        sound_key = f'charge_release_{level}'
        self.sounds[sound_key].play()

    def play_force_toggle(self):
        """Play Force toggle sound"""
        if self.enabled and not self.muted:
            self.sounds['force_toggle'].play()

    def play_force_absorb(self):
        """Play Force bullet absorption sound"""
        if self.enabled and not self.muted:
            self.sounds['force_absorb'].play()

    def play_explosion(self, size='normal'):
        """Play explosion sound"""
        if self.enabled and not self.muted:
            self.sounds['explosion'].play()

    def play_enemy_shoot(self):
        """Play enemy shoot sound"""
        if self.enabled and not self.muted:
            self.sounds['enemy_shoot'].play()

    def play_powerup(self):
        """Play powerup collection sound"""
        if self.enabled and not self.muted:
            self.sounds['powerup'].play()

    def play_player_hit(self):
        """Play player hit sound"""
        if self.enabled and not self.muted:
            self.sounds['player_hit'].play()

    def play_game_over(self):
        """Play game over sound"""
        if self.enabled and not self.muted:
            self.sounds['game_over'].play()

    def play_wave_change(self):
        """Play wave change sound"""
        if self.enabled and not self.muted:
            self.sounds['wave_change'].play()

    def set_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)

    def toggle_mute(self):
        """Toggle mute on/off"""
        self.muted = not self.muted
        print(f"Sound: {'MUTED' if self.muted else 'UNMUTED'}")


# Test the sound manager
if __name__ == "__main__":
    import time

    print("Testing SoundManager...")
    sm = SoundManager()

    print("Player shoot...")
    sm.play_player_shoot()
    time.sleep(0.5)

    print("Explosion...")
    sm.play_explosion()
    time.sleep(1)

    print("Powerup...")
    sm.play_powerup()
    time.sleep(0.5)

    print("Charge level 3...")
    sm.play_charge_release(3)
    time.sleep(0.5)

    print("Done!")
