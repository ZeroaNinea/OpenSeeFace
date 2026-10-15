import time

import numpy as np
import sounddevice as sd

def list_audio_devices():
    """Print available audio input devices."""
    devices = sd.query_devices()

    print("Available audio input devices:")

    for index, device in enumerate(devices):
        if device["max_input_channels"] > 0:
            print(
                f"  {index}: {device['name']} "
                f"(channels: {device['max_input_channels']}, "
                f"default sample rate: {device['default_samplerate']})"
            )

def get_default_input_device():
    """Return the default input device, if one is available."""
    device = sd.default.device
    input_device = device[0]

    if input_device is not None and input_device >= 0:
        info = sd.query_devices(input_device)

        if info["max_input_channels"] > 0:
            return input_device

    # Fall back to the first available input device.
    for index, info in enumerate(sd.query_devices()):
        if info["max_input_channels"] > 0:
            return index

    raise RuntimeError("No audio input devices are available.")

def test_microphone(device=None, duration=5):
    """Print the microphone's RMS audio level for a few seconds."""
    if device is None:
        device = get_default_input_device()

    sample_rate = 48000
    block_size = 1024

    print(f"Using audio device {device}.")
    print("Speak normally, then remain quiet.")

    with sd.InputStream(
        device=device,
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        blocksize=block_size,
    ) as stream:
        start = time.monotonic()

        while time.monotonic() - start < duration:
            audio, overflowed = stream.read(block_size)

            rms = float(np.sqrt(np.mean(np.square(audio))))
            peak = float(np.max(np.abs(audio)))
            max_sample = float(np.max(audio))

            # print(f"\rRMS: {rms:.6f}", end="", flush=True)

            print(
                f"\rRMS: {rms:.6f} | "
                f"Peak: {peak:.6f} | "
                f"Max sample: {max_sample:.6f}",
                end="",
                flush=True,
            )

            if overflowed:
                print("\nWarning: audio input overflowed.")

        print("\nMicrophone test finished.")

# if __name__ == "__main__":
#     list_audio_devices()
#     print()

#     try:
#         test_microphone()
#     except (sd.PortAudioError, RuntimeError) as error:
#         print(f"Microphone test failed: {error}")

if __name__ == "__main__":
    list_audio_devices()
    print()

    try:
        test_microphone(device=29, duration=10)
    except (sd.PortAudioError, RuntimeError) as error:
        print(f"Microphone test failed: {error}")
