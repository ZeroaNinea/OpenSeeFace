"""Audio-based mouth movement for OpenSeeFace."""

import threading

import numpy as np
import sounddevice as sd


def list_audio_devices():
    """Print available audio input devices."""
    print("Available audio input devices:")

    for index, device in enumerate(sd.query_devices()):
        if device["max_input_channels"] > 0:
            print(
                f"  {index}: {device['name']} "
                f"(channels: {device['max_input_channels']}, "
                f"default sample rate: {device['default_samplerate']})"
            )


def get_default_input_device():
    """Return the default input device, falling back to another input."""
    default_device = sd.default.device

    if default_device is not None:
        input_device = default_device[0]

        if input_device is not None and input_device >= 0:
            info = sd.query_devices(input_device)

            if info["max_input_channels"] > 0:
                return input_device

    for index, info in enumerate(sd.query_devices()):
        if info["max_input_channels"] > 0:
            return index

    raise RuntimeError("No audio input devices are available.")


class AudioMouthController:
    """Capture microphone audio and estimate mouth openness."""

    def __init__(
        self,
        device=None,
        threshold=0.12,
        max_level=0.2,
        samplerate=48000,
        blocksize=1024,
    ):
        if threshold <= 0:
            raise ValueError("Audio threshold must be positive.")

        if max_level <= threshold:
            raise ValueError("Maximum audio level must exceed the speech threshold.")

        if device is None:
            device = get_default_input_device()

        self.device = device
        self.device_name = sd.query_devices(device)["name"]
        self.threshold = threshold
        self.release_threshold = threshold * 0.65
        self.max_level = max_level

        self._lock = threading.Lock()
        self._speaking = False
        self._level = 0.0
        self._mouth_open = 0.0

        self.stream = sd.InputStream(
            device=device,
            samplerate=samplerate,
            channels=1,
            dtype="float32",
            blocksize=blocksize,
            callback=self._audio_callback,
        )

        self.stream.start()

    def _audio_callback(self, indata, frames, time_info, status):
        """Calculate audio activity whenever a microphone block arrives."""
        samples = np.asarray(indata[:, 0], dtype=np.float64)

        if not np.all(np.isfinite(samples)):
            return

        # Remove the DC offset before measuring audio activity.
        samples = samples - np.mean(samples)

        level = float(np.sqrt(np.mean(np.square(samples))))

        with self._lock:
            self._level = level

            # Hysteresis prevents the speaking state from flickering.
            if self._speaking:
                if level < self.release_threshold:
                    self._speaking = False
            elif level >= self.threshold:
                self._speaking = True

            print("Level: ", level)

            if self._speaking:
                print("Speaking!", self._speaking)
                target = np.clip(
                    (level - self.threshold) / (self.max_level - self.threshold),
                    0.0,
                    1.0,
                )
            else:
                target = 0.0

            # Smooth the movement without adding much latency.
            self._mouth_open += 0.45 * (target - self._mouth_open)

    def get_state(self):
        """Return (speaking, mouth_open, audio_level)."""
        with self._lock:
            return (
                self._speaking,
                self._mouth_open,
                self._level,
            )

    def close(self):
        """Stop and release the microphone."""
        self.stream.stop()
        self.stream.close()
