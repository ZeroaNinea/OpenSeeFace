# Additions

This repositor is a fork of the OpenSeeFace project. Currently it contains an additional audio mouth tracking script. You can view the commands to controll the feature by using the `python facetracker.py --help` command. It uses the `sounddevice` library to access your input devices.

## Integration with OBS Studio on Linux

If you can't use PipeWire or PulseAudio input, you can only use the ALSA input for both mouth tracking and OBS Studio.

### Create a Virtual Audio Output

However, if you won't apply specific settings, the OBS Studio and the mouth tracking script will conflict with each other. That's why first install `pactl`:

```bash
sudo apt install pactl
```

Now create a virtual audio output:

```bash
pactl load-module module-null-sink \
  sink_name=mouthtrack \
  sink_properties=device.description=MouthTrack
```

Confirm that it exists:

```bash
pactl list short sinks
```

Then find its monitor source:

```bash
pactl list short sources
```

If the sink was created suffessfully, this monitor should be available to capture audio sent to the virtual sink in OBS Studio.

Now configure the OBS Studio:

1. Open OBS Studio -> Settings -> Audio.
2. Then follow Advanced -> Monitoring Device (the exact layout may vary).
3. Select `MouthTrack` as the monitoring device.
4. Click Apply.

Next open Edit -> Advanced Audio Properties. Find your ALSA microphone source, and Audio Monitoring setting to Monitoring Enabled.

### Use the Output in OpenSeeFace (Audio Mouth Tracking Script)

Check the available devices:

```bash
python facetracker.py --list-audio-devices
```

Now use the virtual audio output to run OpenSeeFace with audio mouth tracking:

```bash
python3 facetracker.py \
  --audio-mouth \
  --audio-threshold 0.12 \
  --audio-max-level 10 \
  --audio-device DEVICE_INDEX
```

### Remove the Virtual Audio Output

To remove it you can use this command:

```bash
pactl unload-module THE_ID_OF_THE_OUTPUT
```

You can see its ID after the creation.

It also may be removed after restarting or sutting down the computer.

You can also revert all changes in OBS Studio, but I don't recommend to do that, unless you still plan to use the audio mouth tracker in the future.
