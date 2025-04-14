try:
    import sounddevice as sd
    print("sounddevice module imported successfully")
    print(f"sounddevice version: {sd.__version__}")
    
    # List available audio devices
    print("\nAvailable audio devices:")
    print(sd.query_devices())
    
    # Show default devices
    print("\nDefault input device:", sd.default.device[0])
    print("Default output device:", sd.default.device[1])
    
    print("\nSounddevice is working correctly.")
except ImportError as e:
    print(f"Error importing sounddevice: {e}")
except Exception as e:
    print(f"Error with sounddevice: {e}") 