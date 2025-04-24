import os
import logging
import ffmpeg 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from dotenv import load_dotenv
import speech_recognition as sr

from modules.speech_to_text import transcribe_speech
from modules.email_generator import generate_email
from utils.contact_lookup import get_email_from_name
from modules.send_email import send_email
from modules.feedback import get_feedback

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# In-memory storage for pending emails
pending_emails = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me a voice message to compose an email!")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recognizer = sr.Recognizer()
    user_id = update.message.from_user.id

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    ogg_file = f"voice_{voice.file_id}.ogg"
    wav_file = f"voice_{voice.file_id}.wav"

    try:
        # Download OGG file
        await file.download_to_drive(ogg_file)

        # Convert OGG to WAV using ffmpeg-python
        ffmpeg_bin = r"C:\ffmpeg\bin\ffmpeg.exe"  # Full path to ffmpeg
        stream = ffmpeg.input(ogg_file)
        stream = ffmpeg.output(stream, wav_file)
        ffmpeg.run(stream, cmd=ffmpeg_bin)

        # Transcribe WAV using SpeechRecognition
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        await update.message.reply_text(f"📝 Transcribed: {text}")

        # Generate email using updated function
        recipient_name, recipient_email, subject, body = generate_email(text)

        if not recipient_email:
            await update.message.reply_text(f"❌ Contact '{recipient_name}' not found.")
            return

        email_data = {
            'recipient': recipient_name,
            'recipient_email': recipient_email,
            'subject': subject,
            'body': body
        }
        pending_emails[user_id] = email_data

        # Ask for confirmation
        confirm_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Confirm", callback_data="confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]])

        await update.message.reply_text(
            f"📨 Email Preview:\n\nTo: {recipient_email}\nSubject: {subject}\n\n{body}",
            reply_markup=confirm_markup
        )

    except sr.UnknownValueError:
        await update.message.reply_text("❌ Sorry, I couldn't understand the audio.")
    except sr.RequestError as e:
        await update.message.reply_text(f"⚠️ Could not request results; {e}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")
    finally:
        for f in [ogg_file, wav_file]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except PermissionError:
                    pass

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    if query.data == "confirm":
        email_data = pending_emails.get(user_id)

        if not email_data:
            await query.edit_message_text("⚠️ No email found to confirm.")
            return

        # Send Email
        send_email(
            to=email_data['recipient_email'],  # Correct 'to' parameter
            subject=email_data['subject'],     # Correct 'subject' parameter
            body=email_data['body']            # Correct 'body' parameter
        )

        # Send Feedback
        get_feedback(email_data['recipient_email'])

        await query.edit_message_text("✅ Email sent successfully!")
        pending_emails.pop(user_id, None)

    elif query.data == "cancel":
        pending_emails.pop(user_id, None)
        await query.edit_message_text("❌ Email canceled.")

def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(CallbackQueryHandler(handle_confirmation))

    print("🤖 Telegram Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
