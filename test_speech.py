from dotenv import load_dotenv
import os
from modules.speech_to_text import transcribe_speech

# Load environment variables from .env file
load_dotenv()

print("\n===== SPEECH-TO-TEXT TEST =====")
print("This test will use ElevenLabs if the API key is set correctly,")
print("otherwise it will fall back to Google Speech Recognition.")
print("===============================\n")

# Call the transcribe_speech function
print("Please speak when prompted...")
text = transcribe_speech()

print("\n===============================")
print(f"Transcribed text: '{text}'")
print("Test complete!") 