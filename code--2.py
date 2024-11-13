import pyttsx3

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

# Get available voices
voices = engine.getProperty('voices')

# Set the voice to Male (typically voice[0] or the first voice)
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 150)  # Set speed of speech

# Speak in Male voice
engine.say("This is the male voice.")
engine.runAndWait()

# Set the voice to Female (typically voice[1] or the second voice)
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 150)  # Set speed of speech

# Speak in Female voice
engine.say("This is the female voice.")
engine.runAndWait()

# Close the engine after use
engine.stop()
