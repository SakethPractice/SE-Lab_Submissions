"""Small procedural sound effects used by the game.

Generating the sounds at runtime keeps the project self-contained: no audio
assets need to be downloaded alongside the code.
"""

from array import array
import math

import pygame


class SoundEffects:
    """Create and play short tones, or silently disable audio if unavailable."""

    def __init__(self):
        self.effects = {}
        mixer_settings = pygame.mixer.get_init()
        if not mixer_settings:
            return

        sample_rate, sample_format, channels = mixer_settings
        # The game configures pygame for signed 16-bit samples.  Avoid feeding
        # incompatible raw sample data to an unusual mixer configuration.
        if sample_format != -16:
            return

        try:
            self.effects = {
                "flap": self._tone(sample_rate, channels, 720, 920, 0.07, 0.20),
                "score": self._tone(sample_rate, channels, 880, 1180, 0.10, 0.24),
                "die": self._tone(sample_rate, channels, 360, 120, 0.28, 0.28),
            }
        except pygame.error:
            # The game remains playable on systems without an audio device.
            self.effects = {}

    @staticmethod
    def _tone(sample_rate, channels, start_hz, end_hz, duration, volume):
        sample_count = int(sample_rate * duration)
        samples = array("h")
        phase = 0.0

        for index in range(sample_count):
            progress = index / sample_count
            frequency = start_hz + (end_hz - start_hz) * progress
            phase += 2 * math.pi * frequency / sample_rate
            # A short fade in/out prevents clicks at the ends of each tone.
            envelope = min(1.0, index / (sample_rate * 0.01),
                           (sample_count - index) / (sample_rate * 0.02))
            value = int(32767 * volume * envelope * math.sin(phase))
            samples.extend([value] * channels)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name):
        sound = self.effects.get(name)
        if sound:
            sound.play()
