# import time

# import numpy as np
# import sounddevice as sd

# def list_audio_devices():
#     """Print available audio input devices."""
#     devices = sd.query_devices()

#     print("Available audio input devices:")

#     for index, device in enumerate(devices):
#         if device["max_input_channels"] > 0:
#             print(
#                 f"  {index}: {device['name']} "
#                 f"(channels: {device['max_input_channels']}, "
#                 f"default sample rate: {device['default_samplerate']})"
#             )

# def get_default_input_device():
#     """Return the default input device, if one is available."""
#     device = sd.default.device
#     input_device = device[0]

#     if input_device is not None and input_device >= 0:
#         info = sd.query_devices(input_device)

#         if info["max_input_channels"] > 0:
#             return input_device

#     # Fall back to the first available input device.
#     for index, info in enumerate(sd.query_devices()):
#         if info["max_input_channels"] > 0:
#             return index

#     raise RuntimeError("No audio input devices are available.")

# # def test_microphone(device=None, duration=5):
# #     """Print the microphone's RMS audio level for a few seconds."""
# #     if device is None:
# #         device = get_default_input_device()

# #     sample_rate = 48000
# #     block_size = 1024

# #     print(f"Using audio device {device}.")
# #     print("Speak normally, then remain quiet.")

# #     with sd.InputStream(
# #         device=device,
# #         samplerate=sample_rate,
# #         channels=1,
# #         dtype="float32",
# #         blocksize=block_size,
# #     ) as stream:
# #         start = time.monotonic()

# #         while time.monotonic() - start < duration:
# #             audio, overflowed = stream.read(block_size)

# #             rms = float(np.sqrt(np.mean(np.square(audio))))
# #             peak = float(np.max(np.abs(audio)))
# #             max_sample = float(np.max(audio))

# #             # print(f"\rRMS: {rms:.6f}", end="", flush=True)

# #             print(
# #                 f"\rRMS: {rms:.6f} | "
# #                 f"Peak: {peak:.6f} | "
# #                 f"Max sample: {max_sample:.6f}",
# #                 end="",
# #                 flush=True,
# #             )

# #             if overflowed:
# #                 print("\nWarning: audio input overflowed.")

# #         print("\nMicrophone test finished.")

# # if __name__ == "__main__":
# #     list_audio_devices()
# #     print()

# #     try:
# #         test_microphone()
# #     except (sd.PortAudioError, RuntimeError) as error:
# #         print(f"Microphone test failed: {error}")

# def test_microphone(device=None, duration=15):
#     """Measure microphone levels over a fixed duration."""
#     if device is None:
#         device = get_default_input_device()

#     sample_rate = 48000
#     block_size = 1024
#     levels = []

#     print(f"Using audio device {device}.")
#     print("First remain quiet, then speak normally, then remain quiet again.")

#     with sd.InputStream(
#         device=device,
#         samplerate=sample_rate,
#         channels=1,
#         dtype="float32",
#         blocksize=block_size,
#     ) as stream:
#         start = time.monotonic()
#         next_report = start

#         while time.monotonic() - start < duration:
#             # audio, overflowed = stream.read(block_size)

#             # samples = audio.astype(np.float64)

#             # mean = float(np.mean(samples))
#             # rms = float(np.sqrt(np.mean(np.square(samples))))
#             # centered_rms = float(np.sqrt(np.mean(np.square(samples - mean))))
#             # peak = float(np.max(np.abs(samples)))

#             # if peak > 1.0:
#             #     print(f"\nWarning: audio sample exceeded 1.0: {peak:.4f}")

#             # levels.append(rms)

#             # now = time.monotonic()

#             # if now >= next_report:
#             #     recent = levels[-20:]

#             #     print(
#             #         f"\rRMS: {rms:.4f} | "
#             #         f"Centered RMS: {centered_rms:.4f} | "
#             #         f"Mean: {mean:.4f} | "
#             #         f"Peak: {peak:.4f}",
#             #         end="",
#             #         flush=True,
#             #     )

#             #     next_report = now + 0.25

#             # if overflowed:
#             #     print("\nWarning: audio input overflowed.")

#             audio, overflowed = stream.read(block_size)

#             if not np.all(np.isfinite(audio)):
#                 print("\nWarning: audio contains NaN or infinity.")

#             if np.max(np.abs(audio)) > 1.0:
#                 print(
#                     f"\nOut-of-range audio samples: "
#                     f"min={np.min(audio):.4f}, "
#                     f"max={np.max(audio):.4f}, "
#                     f"dtype={audio.dtype}, "
#                     f"shape={audio.shape}"
#                 )

#             samples = np.asarray(audio, dtype=np.float64)

#             mean = float(np.mean(samples))
#             centered = samples - mean

#             rms = float(np.sqrt(np.mean(np.square(samples))))
#             centered_rms = float(np.sqrt(np.mean(np.square(centered))))

#             minimum = float(np.min(samples))
#             maximum = float(np.max(samples))
#             peak = float(np.max(np.abs(samples)))

#             now = time.monotonic()

#             levels.append(rms)

#             if now >= next_report:
#                 print(
#                     f"\rRMS: {rms:.4f} | "
#                     f"Centered RMS: {centered_rms:.4f} | "
#                     f"Mean: {mean:.4f} | "
#                     f"Min: {minimum:.4f} | "
#                     f"Max: {maximum:.4f} | "
#                     f"Peak: {peak:.4f}    ",
#                     end="",
#                     flush=True,
#                 )
#                 next_report = now + 0.25

#             # if overflowed:
#             #     print("\nWarning: audio input overflowed.")

#         print("\nMicrophone test finished.")
#         print(f"Overall minimum RMS: {min(levels):.4f}")
#         print(f"Overall average RMS: {np.mean(levels):.4f}")
#         print(f"Overall maximum RMS: {max(levels):.4f}")

# if __name__ == "__main__":
#     list_audio_devices()
#     print()

#     try:
#         test_microphone(device=24, duration=10)
#     except (sd.PortAudioError, RuntimeError) as error:
#         print(f"Microphone test failed: {error}")

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
        max_level=0.8,
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

            if self._speaking:
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
