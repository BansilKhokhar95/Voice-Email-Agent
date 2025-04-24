import os
import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
from dotenv import load_dotenv

# def transcribe_speech():
#     """
#     Records speech and transcribes it using ElevenLabs API.
#     """
#     # Load environment variables and get API key
#     load_dotenv()
#     api_key = os.getenv("ELEVENLABS_API_KEY")
    
#     # Record audio
#     print("🎙️ Speak now... (recording for 10 seconds)")
#     samplerate = 16000
#     duration = 10  # seconds
    
#     try:
#         # Record audio from microphone
#         recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
#         sd.wait()
#         print("✅ Recording complete")
        
#         # Save to temporary file
#         with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
#             temp_path = temp_file.name
#             wav.write(temp_path, samplerate, recording)
            
#             # Send to ElevenLabs for transcription
#             print("Transcribing with ElevenLabs...")
#             url = "https://api.elevenlabs.io/v1/speech-to-text"
            
#             with open(temp_path, "rb") as audio_file:
#                 response = requests.post(
#                     url,
#                     headers={"xi-api-key": api_key},
#                     files={"file": audio_file},
#                     data={"model_id": "scribe_v1",
#                           "language": "en"},
#                     timeout=10
#                 )
            
#             # Process response
#             if response.status_code == 200:
#                 result = response.json()
#                 text = result.get("text", "")
#                 if text:
#                     print(f"📝 Transcribed: {text}")
#                     return text
#                 else:
#                     print("❌ No text was transcribed.")
#             else:
#                 print(f"❌ API error: {response.status_code} - {response.text}")
                
#             return ""
            
#     except Exception as e:
#         print(f"❌ Error: {str(e)}")
#         return ""
        
#     finally:
#         # Clean up temporary file if it exists
#         if 'temp_path' in locals() and os.path.exists(temp_path):
#             os.remove(temp_path)

def transcribe_speech():
    """
    Transcribe speech using Google's speech recognition.
    """
    try:
        import speech_recognition as sr
        
        print("🎤 Using Google Speech Recognition...")
        recognizer = sr.Recognizer()
        
        with sr.Microphone() as source:
            print("🎙️ Speak now...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            text = recognizer.recognize_google(audio)
            print(f"📝 Transcribed with Google: {text}")
            return text
    except Exception as e:
        print(f"❌ Google speech recognition failed: {e}")
        return ""



# def transcribe_speech(audio_file_path):
#     """
#     Transcribe speech from an audio file using Google's speech recognition.
#     """
#     try:
#         print("🎤 Using Google Speech Recognition...")

#         recognizer = sr.Recognizer()

#         # Open the audio file
#         with sr.AudioFile(audio_file_path) as source:
#             print("🔉 Processing audio file...")
#             audio = recognizer.record(source)  # Read the entire audio file

#         # Use Google's recognition service to transcribe the audio
#         text = recognizer.recognize_google(audio)
#         print(f"📝 Transcribed with Google: {text}")
#         return text

#     except sr.UnknownValueError:
#         print("❌ Could not understand the audio.")
#         return "Sorry, I could not understand the audio."
    
#     except sr.RequestError as e:
#         print(f"❌ Error with the speech recognition service; {e}")
#         return "Could not request results from Google Speech Recognition service."

#     except Exception as e:
#         print(f"❌ An error occurred during transcription: {e}")
#         return "An error occurred while transcribing the audio."