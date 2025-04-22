from modules.speech_to_text import transcribe_speech

if __name__ == "__main__":
    text = transcribe_speech()
    if text:
        print(f"\n✅ Final Transcription: {text}")
    else:
        print("\n⚠️ No transcription returned.")