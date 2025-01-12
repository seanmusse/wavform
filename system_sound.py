import sounddevice as sd
import numpy as np

# WASAPI loopback example
def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = indata

try:
    device = None
    for idx, dev in enumerate(sd.query_devices()):
        if dev['hostapi'] == sd.WASAPI_HOSTAPI and 'loopback' in dev['name'].lower():
            device = idx
            break

    if device is None:
        raise RuntimeError("No WASAPI loopback device found.")

    samplerate = sd.query_devices(device, 'input')['default_samplerate']
    with sd.Stream(device=(device, device), samplerate=samplerate, channels=2, callback=callback):
        print("Listening and playing back system audio... Press Ctrl+C to stop.")
        while True:
            pass

except Exception as e:
    print(f"Error: {e}")
