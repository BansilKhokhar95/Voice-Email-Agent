# Voice Email Agent

A Streamlit application that allows users to send emails using voice commands. This app uses speech recognition to transcribe voice input, generates email content using AI, and sends emails through Gmail API.

## Features

- Voice command transcription using SpeechRecognition
- AI-powered email content generation using LangChain and LangGraph
- Contact lookup functionality from Google Sheets
- Email preview and confirmation
- Secure email sending via Gmail API
- Telegram bot integration for remote access

## Technologies

- **Frontend**: Streamlit
- **Speech Recognition**: SpeechRecognition, PyAudio
- **AI**: LangChain, LangGraph, Groq
- **Email**: Google API (Gmail)
- **Text-to-Speech**: ElevenLabs, pyttsx3
- **Other**: Python, dotenv for environment variables

## Project Structure

- `app.py`: Main Streamlit application
- `telegram_bot.py`: Telegram bot implementation
- `run_bot.py`: Bot runner script
- `modules/`: Core functionality modules
  - `speech_to_text.py`: Voice transcription
  - `email_generator.py`: Email content generation
  - `send_email.py`: Email sending functionality
  - `user_confirmation.py`: User confirmation handling
  - `feedback.py`: User feedback processing
- `utils/`: Utility functions
  - `gmail_auth.py`: Gmail API authentication
  - `contact_lookup.py`: Contact information lookup from Google Sheets

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following:
   ```
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_API_KEY=your_google_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ```
4. Set up Google API credentials:
   - Place `credentials.json` for Gmail API access
   - Place `token_sheets.json` for Google Sheets access
5. Run the application:
   ```
   streamlit run app.py
   ```
6. For Telegram bot:
   ```
   python run_bot.py
   ```

## Usage

1. Click "Activate Assistant" to start recording your voice
2. Speak your email request (e.g., "Send an email to John about the meeting tomorrow")
3. Review the generated email content
4. Confirm to send or cancel

## License

See the LICENSE file for details.
