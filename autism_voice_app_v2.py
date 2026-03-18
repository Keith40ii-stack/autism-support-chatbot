import os
import time
import json
import tempfile
import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Jayden’s Calm Journey | Autism Support Chatbot",
    page_icon="🎈",
    layout="centered"
)

# --------------------------------------------------
# App Store-style UI
# --------------------------------------------------
st.markdown("""
<style>
/* ---------- Global ---------- */
.stApp {
    background: linear-gradient(180deg, #dff3ff 0%, #edf9ff 45%, #f8fdff 100%);
    overflow: hidden;
    color: #163240;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

section.main > div {
    padding-top: 1rem;
}

/* ---------- Balloon background ---------- */
.balloon-bg {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.balloon {
    position: absolute;
    bottom: -150px;
    width: 74px;
    height: 96px;
    border-radius: 50% 50% 45% 45%;
    opacity: 0.20;
    animation-name: floatUp;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    filter: blur(0.2px);
}

.balloon::after {
    content: "";
    position: absolute;
    left: 50%;
    top: 94px;
    width: 2px;
    height: 72px;
    background: rgba(110, 130, 145, 0.22);
    transform: translateX(-50%);
}

.b1 { left: 5%;  background: #8fd3ff; animation-duration: 19s; animation-delay: 0s; }
.b2 { left: 16%; background: #ffd8e8; animation-duration: 24s; animation-delay: 3s; }
.b3 { left: 29%; background: #ffe49f; animation-duration: 22s; animation-delay: 1s; }
.b4 { left: 43%; background: #bde7c8; animation-duration: 25s; animation-delay: 5s; }
.b5 { left: 58%; background: #cfc8ff; animation-duration: 20s; animation-delay: 2s; }
.b6 { left: 74%; background: #ffcfb3; animation-duration: 26s; animation-delay: 6s; }
.b7 { left: 89%; background: #aee6ff; animation-duration: 23s; animation-delay: 4s; }

@keyframes floatUp {
    0% {
        transform: translateY(0) translateX(0px);
        opacity: 0;
    }
    10% {
        opacity: 0.22;
    }
    50% {
        transform: translateY(-52vh) translateX(12px);
    }
    100% {
        transform: translateY(-120vh) translateX(-10px);
        opacity: 0;
    }
}

/* ---------- Main container ---------- */
.block-container {
    position: relative;
    z-index: 1;
    max-width: 760px;
    background: rgba(255,255,255,0.86);
    border-radius: 30px;
    padding: 1.4rem 1.25rem 2rem 1.25rem;
    margin-top: 0.75rem;
    margin-bottom: 1rem;
    box-shadow: 0 18px 40px rgba(43, 91, 122, 0.10);
    backdrop-filter: blur(10px);
}

/* ---------- Typography ---------- */
.app-brand {
    text-align: center;
    font-size: 2rem;
    font-weight: 800;
    color: #17384b;
    margin-bottom: 0.2rem;
    letter-spacing: -0.02em;
}

.app-subbrand {
    text-align: center;
    font-size: 1rem;
    font-weight: 600;
    color: #4b6f82;
    margin-bottom: 0.3rem;
}

.app-caption {
    text-align: center;
    color: #6a8998;
    margin-bottom: 1rem;
    font-size: 0.95rem;
}

.hero-card {
    background: linear-gradient(135deg, #d8eefb 0%, #eef8ff 100%);
    border-radius: 24px;
    padding: 1.1rem 1rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
    margin-bottom: 1rem;
}

.soft-card {
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(190, 220, 235, 0.65);
    border-radius: 22px;
    padding: 1rem 1rem;
    box-shadow: 0 10px 22px rgba(45, 82, 104, 0.06);
    margin-bottom: 0.9rem;
}

.card-title {
    font-size: 1.25rem;
    font-weight: 750;
    color: #1f4255;
    margin-bottom: 0.25rem;
}

.card-text {
    color: #5a7886;
    line-height: 1.55;
    font-size: 0.98rem;
}

/* ---------- Buttons ---------- */
.stButton > button {
    width: 100%;
    border-radius: 18px;
    min-height: 3.25rem;
    font-size: 1rem;
    font-weight: 700;
    border: none;
    background: linear-gradient(180deg, #d6eef9 0%, #cbe8f7 100%);
    color: #1d3a4b;
    box-shadow: 0 6px 14px rgba(67, 131, 168, 0.10);
}

.stButton > button:hover {
    background: linear-gradient(180deg, #c8e8f8 0%, #bce1f4 100%);
    color: #17384b;
}

.stButton > button:focus {
    outline: none;
    box-shadow: 0 0 0 0.2rem rgba(151, 209, 239, 0.35);
}

/* ---------- Inputs ---------- */
[data-testid="stAudioInput"] {
    background: rgba(255,255,255,0.9);
    border-radius: 20px;
    padding: 0.4rem;
}

/* ---------- Alerts ---------- */
[data-testid="stSuccess"] {
    border-radius: 18px;
}

[data-testid="stInfo"] {
    border-radius: 18px;
}

/* ---------- Divider space ---------- */
hr {
    margin-top: 1.2rem;
    margin-bottom: 1.2rem;
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

# --------------------------------------------------
# Browser speech
# --------------------------------------------------
def speak_text(text: str):
    safe_text = json.dumps(text)
    js_code = f"""
    <script>
    const text = {safe_text};
    const utterance = new SpeechSynthesisUtterance(text);

    utterance.rate = 0.96;
    utterance.pitch = 1.14;
    utterance.volume = 1.0;

    function pickVoice() {{
        const voices = window.speechSynthesis.getVoices();
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

        if (!chosenVoice) {{
            chosenVoice = voices.find(v => v.lang && v.lang.startsWith("en"));
        }}

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

# --------------------------------------------------
# Audio transcription
# --------------------------------------------------
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

# --------------------------------------------------
# Intent interpretation
# --------------------------------------------------
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

# --------------------------------------------------
# Emotion responses
# --------------------------------------------------
def get_response(emotion: str):
    responses = {
        "happy": "I’m so glad you feel happy. That makes me smile.",
        "sad": "It’s okay to feel sad. I’m here with you. Let’s take a slow breath together.",
        "angry": "I see you’re feeling angry. That’s okay. Let’s pause and take a deep breath together.",
        "scared": "You are safe right now. I’m here with you. Let’s take a calm breath together."
    }
    return responses.get(emotion, "I’m here to help you. You’re doing a great job.")

# --------------------------------------------------
# Session state
# --------------------------------------------------
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

# --------------------------------------------------
# Emotion map
# --------------------------------------------------
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

# --------------------------------------------------
# Navigation helpers
# --------------------------------------------------
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

# --------------------------------------------------
# Branded header
# --------------------------------------------------
st.markdown("<div class='app-brand'>🎈 Jayden’s Calm Journey</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subbrand'>Autism Support Chatbot</div>", unsafe_allow_html=True)
st.markdown("<div class='app-caption'>A gentle space to help children feel calm, safe, and understood.</div>", unsafe_allow_html=True)

if st.button("🔊 Test Voice Output"):
    speak_text("Hello, friend. I am here to help you.")
    st.success("Voice test triggered.")

screen = st.session_state.screen

# --------------------------------------------------
# Home
# --------------------------------------------------
if screen == "home":
    st.markdown("""
    <div class='hero-card'>
        <div class='card-title'>Hello, Friend 😊</div>
        <div class='card-text'>Choose one activity to begin your calm journey.</div>
    </div>
    """, unsafe_allow_html=True)

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

# --------------------------------------------------
# Feelings
# --------------------------------------------------
elif screen == "feelings":
    st.markdown("""
    <div class='soft-card'>
        <div class='card-title'>How do you feel?</div>
        <div class='card-text'>Tap a feeling and I will help.</div>
    </div>
    """, unsafe_allow_html=True)

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

# --------------------------------------------------
# Response
# --------------------------------------------------
elif screen == "response":
    selected = st.session_state.selected_emotion

    st.markdown(f"""
    <div class='soft-card'>
        <div class='card-title'>{selected['emoji']} {selected['heading']}</div>
        <div class='card-text'>{selected['body']}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶ Listen Again", use_container_width=True):
        speak_text(selected["heading"] + " " + selected["body"])

    if st.button("🧘 Calm Down", use_container_width=True):
        go("calm")

    if st.button("🏠 Home", use_container_width=True):
        go("home")

# --------------------------------------------------
# Speak for Me
# --------------------------------------------------
elif screen == "speak":
    st.markdown("""
    <div class='soft-card'>
        <div class='card-title'>🔊 Speak for Me</div>
        <div class='card-text'>Tap a button and I will say the words out loud for you.</div>
    </div>
    """, unsafe_allow_html=True)

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

# --------------------------------------------------
# Calm down
# --------------------------------------------------
elif screen == "calm":
    st.markdown("""
    <div class='soft-card'>
        <div class='card-title'>🧘 Breathe with me</div>
        <div class='card-text'>Inhale... Exhale...</div>
    </div>
    """, unsafe_allow_html=True)

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

# --------------------------------------------------
# Routine
# --------------------------------------------------
elif screen == "routine":
    st.markdown("""
    <div class='soft-card'>
        <div class='card-title'>📅 My Routine</div>
        <div class='card-text'>Visual steps make transitions easier.</div>
    </div>
    """, unsafe_allow_html=True)

    steps = [
        "🪥 Brush Teeth",
        "👕 Get Dressed",
        "🍽 Eat Breakfast",
        "🎒 Go to School"
    ]

    for step in steps:
        st.markdown(f"<div class='soft-card'><div class='card-text'>{step}</div></div>", unsafe_allow_html=True)

    if st.button("➡ Next Step", use_container_width=True):
        st.success("Great job. Keep going.")
        speak_text("Great job. Keep going.")

    if st.button("🏠 Home", use_container_width=True):
        go("home")

# --------------------------------------------------
# Practice talking
# --------------------------------------------------
elif screen == "talking":
    st.markdown("""
    <div class='soft-card'>
        <div class='card-title'>💬 Practice Talking</div>
        <div class='card-text'>Let’s practice simple words together.</div>
    </div>
    """, unsafe_allow_html=True)

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

    st.markdown("""
    <div class='soft-card'>
        <div class='card-title'>🎤 Talk to me</div>
        <div class='card-text'>Press and record your voice so I can help understand your words.</div>
    </div>
    """, unsafe_allow_html=True)

    audio = st.audio_input("Record your voice")

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