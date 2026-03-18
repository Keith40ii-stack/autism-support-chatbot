import os
import time
import tempfile
import streamlit as st
import pyttsx3
import speech_recognition as sr

# -----------------------------
# App configuration
# -----------------------------
st.set_page_config(
    page_title="Autism Support Chatbot",
    page_icon="🌈",
    layout="centered"
)

# -----------------------------
# Debug info
# -----------------------------
st.write("DEBUG FILE:", os.path.abspath(__file__))
st.write("DEBUG VERSION: KID FRIENDLY VOICE + SPEAK SCREEN BUILD")

# -----------------------------
# Voice selection helper
# -----------------------------
def get_best_voice_id(engine):
    voices = engine.getProperty("voices")
    if not voices:
        return None

    preferred_names = ["zira", "female", "hazel", "susan"]
    fallback_names = ["david", "male"]

    # First pass: kid-friendlier / softer voices
    for preferred in preferred_names:
        for voice in voices:
            voice_name = getattr(voice, "name", "").lower()
            if preferred in voice_name:
                return voice.id

    # Second pass: anything not obviously male if possible
    for voice in voices:
        voice_name = getattr(voice, "name", "").lower()
        if not any(word in voice_name for word in fallback_names):
            return voice.id

    # Final fallback: first available
    return voices[0].id

# -----------------------------
# Voice output
# -----------------------------
def speak_text(text):
    try:
        engine = pyttsx3.init()

        # Kid-friendlier pacing
        engine.setProperty("rate", 135)
        engine.setProperty("volume", 0.95)

        best_voice = get_best_voice_id(engine)
        if best_voice:
            engine.setProperty("voice", best_voice)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        st.warning(f"Voice output error: {e}")

# -----------------------------
# Voice input / transcription
# -----------------------------
def transcribe_audio(audio_file):
    try:
        recognizer = sr.Recognizer()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.read())
            temp_path = tmp.name

        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)
        return text

    except sr.UnknownValueError:
        return "I couldn't understand that."
    except Exception as e:
        return f"Error: {e}"

# -----------------------------
# Smart microphone understanding
# -----------------------------
def interpret_child_message(text):
    lowered = text.lower().strip()

    if any(phrase in lowered for phrase in [
        "i am happy", "i'm happy", "happy", "good", "excited", "great"
    ]):
        return {
            "intent": "emotion_happy",
            "response": "I’m so glad you feel happy. That makes me smile."
        }

    if any(phrase in lowered for phrase in [
        "i am sad", "i'm sad", "sad", "crying", "unhappy"
    ]):
        return {
            "intent": "emotion_sad",
            "response": "It’s okay to feel sad. I’m here with you. Let’s take a slow breath together."
        }

    if any(phrase in lowered for phrase in [
        "i am angry", "i'm angry", "angry", "mad", "frustrated", "upset"
    ]):
        return {
            "intent": "emotion_angry",
            "response": "I see you’re feeling angry. That’s okay. Let’s pause and take a deep breath together."
        }

    if any(phrase in lowered for phrase in [
        "i am scared", "i'm scared", "scared", "afraid", "nervous", "worried"
    ]):
        return {
            "intent": "emotion_scared",
            "response": "You are safe right now. I’m here with you. Let’s take a calm breath together."
        }

    if any(phrase in lowered for phrase in [
        "i need help", "help me", "can you help", "help"
    ]):
        return {
            "intent": "need_help",
            "response": "I can help you. Let’s take one small step together."
        }

    if any(phrase in lowered for phrase in [
        "i need a break", "break", "too much", "too loud", "i want a break"
    ]):
        return {
            "intent": "need_break",
            "response": "It is okay to take a break. Let’s breathe and rest for a moment."
        }

    if any(phrase in lowered for phrase in [
        "hello", "hi", "hey"
    ]):
        return {
            "intent": "greeting",
            "response": "Hello, friend. I’m happy to talk with you."
        }

    if any(phrase in lowered for phrase in [
        "i am okay", "i'm okay", "okay", "fine"
    ]):
        return {
            "intent": "okay",
            "response": "I’m glad you told me. Thank you for checking in with me."
        }

    return {
        "intent": "unknown",
        "response": "Thank you for telling me. I am here with you."
    }

# -----------------------------
# Chatbot responses
# -----------------------------
def get_response(emotion):
    responses = {
        "happy": "I’m so glad you feel happy. That makes me smile.",
        "sad": "It’s okay to feel sad. I’m here with you. Let’s take a slow breath together.",
        "angry": "I see you’re feeling angry. That’s okay. Let’s pause and take a deep breath together.",
        "scared": "You are safe right now. I’m here with you. Let’s take a calm breath together."
    }
    return responses.get(emotion, "I’m here to help you. You’re doing a great job.")

# -----------------------------
# Session state
# -----------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "home"

if "selected_emotion" not in st.session_state:
    st.session_state.selected_emotion = {
        "emoji": "😊",
        "heading": "Welcome, friend.",
        "body": "I’m here to help you feel calm and safe."
    }

if "last_spoken_phrase" not in st.session_state:
    st.session_state.last_spoken_phrase = "I need help."

# -----------------------------
# Emotion content
# -----------------------------
emotion_map = {
    "Happy": {
        "emoji": "😊",
        "heading": "I see you feel happy.",
        "body": "That is wonderful. Let’s keep the good feeling going."
    },
    "Sad": {
        "emoji": "😢",
        "heading": "I see you feel sad.",
        "body": "Let’s take a quiet breath together."
    },
    "Angry": {
        "emoji": "😡",
        "heading": "I see you feel angry.",
        "body": "Let’s slow down and take a deep breath."
    },
    "Scared": {
        "emoji": "😨",
        "heading": "I see you feel scared.",
        "body": "You are safe. Let’s breathe together."
    },
}

# -----------------------------
# Navigation helpers
# -----------------------------
def go(screen_name):
    st.session_state.screen = screen_name

def select_emotion(emotion):
    st.session_state.selected_emotion = emotion_map[emotion]
    response = get_response(emotion.lower())
    speak_text(response)
    go("response")

def speak_phrase(phrase):
    st.session_state.last_spoken_phrase = phrase
    speak_text(phrase)

# -----------------------------
# Title / header
# -----------------------------
st.title("Autism Support Chatbot")
st.caption("Kid-friendly voice, communication support, and smart microphone input")

if st.button("🔊 Test Voice Output"):
    speak_text("Hello, friend. I am here to help you.")
    st.success("Voice test triggered.")

screen = st.session_state.screen

# -----------------------------
# Home screen
# -----------------------------
if screen == "home":
    st.subheader("😊 Hello, Friend!")
    st.write("Choose one activity.")

    if st.button("😊 Feelings", use_container_width=True):
        go("feelings")

    if st.button("🔊 Speak for Me", use_container_width=True):
        go("speak")

    if st.button("🧘 Calm Down", use_container_width=True):
        go("calm")

    if st.button("📅 My Routine", use_container_width=True):
        go("routine")

    if st.button("💬 Practice Talking", use_container_width=True):
        go("talking")

# -----------------------------
# Feelings screen
# -----------------------------
elif screen == "feelings":
    st.subheader("How do you feel?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("😊 Happy", use_container_width=True):
            select_emotion("Happy")
        if st.button("😡 Angry", use_container_width=True):
            select_emotion("Angry")

    with col2:
        if st.button("😢 Sad", use_container_width=True):
            select_emotion("Sad")
        if st.button("😨 Scared", use_container_width=True):
            select_emotion("Scared")

    if st.button("🏠 Home", use_container_width=True):
        go("home")

# -----------------------------
# Response screen
# -----------------------------
elif screen == "response":
    selected = st.session_state.selected_emotion

    st.subheader(f"{selected['emoji']} {selected['heading']}")
    st.write(selected["body"])

    if st.button("▶ Listen Again", use_container_width=True):
        speak_text(selected["heading"] + " " + selected["body"])

    if st.button("🧘 Calm Down", use_container_width=True):
        go("calm")

    if st.button("🏠 Home", use_container_width=True):
        go("home")

# -----------------------------
# Speak for Me screen
# -----------------------------
elif screen == "speak":
    st.subheader("🔊 Speak for Me")
    st.write("Tap a phrase and I will say it out loud.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🙋 I need help", use_container_width=True):
            speak_phrase("I need help.")
            st.success('Spoken: "I need help."')

        if st.button("🛑 I need a break", use_container_width=True):
            speak_phrase("I need a break.")
            st.success('Spoken: "I need a break."')

        if st.button("😢 I feel sad", use_container_width=True):
            speak_phrase("I feel sad.")
            st.success('Spoken: "I feel sad."')

        if st.button("😨 I feel scared", use_container_width=True):
            speak_phrase("I feel scared.")
            st.success('Spoken: "I feel scared."')

    with col2:
        if st.button("😊 I feel happy", use_container_width=True):
            speak_phrase("I feel happy.")
            st.success('Spoken: "I feel happy."')

        if st.button("😡 I feel angry", use_container_width=True):
            speak_phrase("I feel angry.")
            st.success('Spoken: "I feel angry."')

        if st.button("👋 Hello", use_container_width=True):
            speak_phrase("Hello.")
            st.success('Spoken: "Hello."')

        if st.button("🙂 I am okay", use_container_width=True):
            speak_phrase("I am okay.")
            st.success('Spoken: "I am okay."')

    st.info(f'Last phrase: "{st.session_state.last_spoken_phrase}"')

    if st.button("🔁 Say Last Phrase Again", use_container_width=True):
        speak_text(st.session_state.last_spoken_phrase)

    if st.button("🏠 Home", use_container_width=True):
        go("home")

# -----------------------------
# Calm screen
# -----------------------------
elif screen == "calm":
    st.subheader("Breathe with me")
    st.write("Inhale... Exhale...")

    progress_bar = st.progress(0)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Done", use_container_width=True):
            st.success("Great job calming your body.")
            speak_text("Great job calming your body.")

    with col2:
        if st.button("🔁 Repeat", use_container_width=True):
            speak_text("Let’s breathe together. Inhale. Exhale.")
            for pct in (20, 40, 60, 80, 100):
                progress_bar.progress(pct)
                time.sleep(0.25)
            progress_bar.progress(0)

    if st.button("🏠 Home", use_container_width=True):
        go("home")

# -----------------------------
# Routine screen
# -----------------------------
elif screen == "routine":
    st.subheader("My Routine")

    steps = [
        "🪥 Brush Teeth",
        "👕 Get Dressed",
        "🍽 Eat Breakfast",
        "🎒 Go to School"
    ]

    for step in steps:
        st.write(step)

    if st.button("➡ Next Step", use_container_width=True):
        st.success("Great job. Keep going.")
        speak_text("Great job. Keep going.")

    if st.button("🏠 Home", use_container_width=True):
        go("home")

# -----------------------------
# Practice Talking screen
# -----------------------------
elif screen == "talking":
    st.subheader("💬 Practice Talking")
    st.write('Bot: "Say hello!"')

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👋 Hello", use_container_width=True):
            st.success("Nice job saying hello.")
            speak_text("Nice job saying hello.")

    with col2:
        if st.button("🙂 Hi", use_container_width=True):
            st.success("Great greeting.")
            speak_text("Great greeting.")

    if st.button("🔁 Try Again", use_container_width=True):
        st.info("Let’s practice again.")
        speak_text("Let’s practice again. Say hello.")

    st.divider()
    st.subheader("🎤 Talk to me")

    audio = st.audio_input("Press and record your voice")

    if audio is not None:
        st.audio(audio)

        if st.button("🧠 Understand My Words", use_container_width=True):
            text = transcribe_audio(audio)
            st.write("You said:", text)

            result = interpret_child_message(text)
            response = result["response"]

            st.success(response)
            speak_text(response)

            if result["intent"] in ["emotion_angry", "emotion_sad", "emotion_scared", "need_break"]:
                st.info("You can also use Calm Down for breathing support.")

    if st.button("🏠 Home", use_container_width=True):
        go("home")