import os
import time
import json
import tempfile
import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr

# -----------------------------
# App configuration
# -----------------------------
st.set_page_config(
    page_title= "Jayden’s Calm Journey | Autism Support Chatbot",
    page_icon="🎈",
    layout="centered"
)

# -----------------------------
# Soft blue background + moving balloons
# -----------------------------
st.markdown("""
<style>
/* Overall app background */
.stApp {
    background: linear-gradient(180deg, #dff4ff 0%, #eefaff 45%, #f8fdff 100%);
    overflow: hidden;
}

/* Floating balloon background */
.balloon-bg {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

/* App content card */
.block-container {
    position: relative;
    z-index: 1;
    background: rgba(255, 255, 255, 0.84);
    border-radius: 24px;
    padding: 2rem;
    margin-top: 1rem;
    box-shadow: 0 8px 24px rgba(35, 80, 110, 0.08);
}

/* Balloon styling */
.balloon {
    position: absolute;
    bottom: -140px;
    width: 70px;
    height: 90px;
    border-radius: 50% 50% 45% 45%;
    opacity: 0.22;
    animation-name: floatUp;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
}

.balloon::after {
    content: "";
    position: absolute;
    left: 50%;
    top: 88px;
    width: 2px;
    height: 70px;
    background: rgba(120, 140, 160, 0.25);
    transform: translateX(-50%);
}

.b1 { left: 6%;  background: #8fd3ff; animation-duration: 20s; animation-delay: 0s; }
.b2 { left: 18%; background: #ffd6e7; animation-duration: 24s; animation-delay: 4s; }
.b3 { left: 31%; background: #ffe49c; animation-duration: 22s; animation-delay: 2s; }
.b4 { left: 47%; background: #bde7c8; animation-duration: 26s; animation-delay: 6s; }
.b5 { left: 63%; background: #cfc7ff; animation-duration: 21s; animation-delay: 1s; }
.b6 { left: 78%; background: #ffcfb3; animation-duration: 25s; animation-delay: 5s; }
.b7 { left: 90%; background: #aee6ff; animation-duration: 23s; animation-delay: 3s; }

@keyframes floatUp {
    0% {
        transform: translateY(0) translateX(0px);
        opacity: 0;
    }
    10% {
        opacity: 0.22;
    }
    50% {
        transform: translateY(-50vh) translateX(12px);
    }
    100% {
        transform: translateY(-120vh) translateX(-10px);
        opacity: 0;
    }
}

/* Buttons */
.stButton > button {
    border-radius: 16px;
    height: 3.2em;
    font-size: 1rem;
    border: none;
    background-color: #d6eef9;
    color: #234;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #bfe4f5;
}

/* Headings */
h1, h2, h3 {
    color: #2b4c5a;
}

/* Info-style blocks */
.custom-note {
    background: rgba(214, 238, 249, 0.65);
    padding: 0.9rem 1rem;
    border-radius: 16px;
    color: #234;
    margin-bottom: 1rem;
}
</style>

<div class="balloon-bg">
    <div class="balloon b1"></div>
    <div class="balloon b2"></div>
    <div class="balloon b3"></div>
    <div class="balloon b4"></div>
    <div class="balloon b5"></div>
    <div class="balloon b6"></div>
    <div class="balloon b7"></div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Debug info
# -----------------------------
st.write("DEBUG FILE:", os.path.abspath(__file__))
st.write("DEBUG VERSION: CLEAN CLOUD BUILD WITH BALLOONS")

# -----------------------------
# Browser-based voice output
# -----------------------------
def speak_text(text: str):
    safe_text = json.dumps(text)

    js_code = f"""
    <script>
    const text = {safe_text};
    const utterance = new SpeechSynthesisUtterance(text);

    // Best balance for a gentle, youthful feel
    utterance.rate = 0.96;
    utterance.pitch = 1.14;
    utterance.volume = 1.0;

    function pickVoice() {{
        const voices = window.speechSynthesis.getVoices();

        // Best available voices to try first
        const preferredNames = [
            "Google US English",
            "Samantha",
            "Microsoft Zira",
            "Karen",
            "Moira",
            "Alex",
            "Eddy",
            "Evan"
        ];

        let chosenVoice = null;

        for (const preferred of preferredNames) {{
            chosenVoice = voices.find(v => v.name && v.name.includes(preferred));
            if (chosenVoice) break;
        }}

        // Fallback to an English voice
        if (!chosenVoice) {{
            chosenVoice = voices.find(v => v.lang && v.lang.startsWith("en"));
        }}

        // Final fallback
        if (!chosenVoice && voices.length > 0) {{
            chosenVoice = voices[0];
        }}

        if (chosenVoice) {{
            utterance.voice = chosenVoice;
        }}

        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
    }}

    if (window.speechSynthesis.getVoices().length === 0) {{
        window.speechSynthesis.onvoiceschanged = pickVoice;
    }} else {{
        pickVoice();
    }}
    </script>
    """
    components.html(js_code, height=0)

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

        return recognizer.recognize_google(audio_data)

    except sr.UnknownValueError:
        return "I couldn't understand that."
    except Exception as e:
        return f"Error: {e}"

# -----------------------------
# Smart microphone understanding
# -----------------------------
def interpret_child_message(text: str):
    lowered = text.lower().strip()

    if any(phrase in lowered for phrase in [
        "i am happy", "i'm happy", "happy", "good", "excited", "great"
    ]):
        return {
            "intent": "emotion_happy",
            "response": "I’m so glad you feel happy. That makes me smile."
        }

    if any(phrase in lowered for phrase in [
        "i am sad", "i'm sad", "sad", "crying", "unhappy", "upset"
    ]):
        return {
            "intent": "emotion_sad",
            "response": "It’s okay to feel sad. I’m here with you. Let’s take a slow breath together."
        }

    if any(phrase in lowered for phrase in [
        "i am angry", "i'm angry", "angry", "mad", "frustrated"
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
# Emotion responses
# -----------------------------
def get_response(emotion: str):
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
    st.session_state.last_spoken_phrase = "Help me, please."

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
def go(screen_name: str):
    st.session_state.screen = screen_name

def select_emotion(emotion: str):
    st.session_state.selected_emotion = emotion_map[emotion]
    response = get_response(emotion.lower())
    speak_text(response)
    go("response")

def speak_phrase(phrase: str):
    st.session_state.last_spoken_phrase = phrase
    speak_text(phrase)

# -----------------------------
# Header
# -----------------------------
st.title("Autism Support Chatbot")
st.caption("A calm, kid-friendly support tool inspired by love, connection, and communication.")

if st.button("🔊 Test Voice Output"):
    speak_text("Hello, friend. I am here to help you.")
    st.success("Voice test triggered.")

screen = st.session_state.screen

# -----------------------------
# Home
# -----------------------------
if screen == "home":
    st.subheader("😊 Hello, Friend!")
    st.markdown("<div class='custom-note'>Choose one activity below.</div>", unsafe_allow_html=True)

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
# Feelings
# -----------------------------
elif screen == "feelings":
    st.subheader("How do you feel?")
    st.markdown("<div class='custom-note'>Tap a feeling and I will help.</div>", unsafe_allow_html=True)

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
# Response
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
# Speak for Me
# -----------------------------
elif screen == "speak":
    st.subheader("🔊 Speak for Me")
    st.markdown(
        "<div class='custom-note'>Tap a button and I will say the words out loud for you.</div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🙋 Help Me", use_container_width=True):
            speak_phrase("Help me, please.")
            st.success('Spoken: "Help me, please."')

        if st.button("🛑 Break Please", use_container_width=True):
            speak_phrase("I need a break, please.")
            st.success('Spoken: "I need a break, please."')

        if st.button("😢 I Feel Sad", use_container_width=True):
            speak_phrase("I feel sad.")
            st.success('Spoken: "I feel sad."')

        if st.button("😨 I Feel Scared", use_container_width=True):
            speak_phrase("I feel scared.")
            st.success('Spoken: "I feel scared."')

    with col2:
        if st.button("😊 I Feel Happy", use_container_width=True):
            speak_phrase("I feel happy.")
            st.success('Spoken: "I feel happy."')

        if st.button("😡 I Feel Angry", use_container_width=True):
            speak_phrase("I feel angry.")
            st.success('Spoken: "I feel angry."')

        if st.button("👋 Hello", use_container_width=True):
            speak_phrase("Hello.")
            st.success('Spoken: "Hello."')

        if st.button("🙂 I Am Okay", use_container_width=True):
            speak_phrase("I am okay.")
            st.success('Spoken: "I am okay."')

    st.info(f'Last phrase: "{st.session_state.last_spoken_phrase}"')

    if st.button("🔁 Say Last Phrase Again", use_container_width=True):
        speak_text(st.session_state.last_spoken_phrase)

    if st.button("🏠 Home", use_container_width=True):
        go("home")

# -----------------------------
# Calm Down
# -----------------------------
elif screen == "calm":
    st.subheader("Breathe with me")
    st.markdown("<div class='custom-note'>Inhale... Exhale...</div>", unsafe_allow_html=True)

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
# Routine
# -----------------------------
elif screen == "routine":
    st.subheader("My Routine")
    st.markdown("<div class='custom-note'>Visual steps make transitions easier.</div>", unsafe_allow_html=True)

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
# Practice Talking
# -----------------------------
elif screen == "talking":
    st.subheader("💬 Practice Talking")
    st.markdown("<div class='custom-note'>Let’s practice simple words together.</div>", unsafe_allow_html=True)

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