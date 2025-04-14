import pyttsx3

def get_feedback(sent: bool):
    engine = pyttsx3.init()
    if sent:
        engine.say("Email sent successfully.")
    else:
        engine.say("Email was not sent.")
    engine.runAndWait()
