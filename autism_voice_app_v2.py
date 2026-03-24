import os
import time
import json
import base64
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
# Helpers
# --------------------------------------------------
def get_base64_image(image_path: str):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None


def speak_text(text: str):
    safe_text = json.dumps(text)
    js_code = f"""
    <script>
    (function() {{
        const text = {safe_text};
        const synth = window.speechSynthesis;

        function speakNow() {{
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.98;
            utterance.pitch = 1.18;
            utterance.volume = 1.0;

            const voices = synth.getVoices();
            const preferredNames = [
                "Samantha",
                "Google US English",
                "Microsoft Zira",
                "Karen",
                "Moira",
                "Alex"
            ];

            let chosenVoice = null;

            for (const preferred of preferredNames) {{
                chosenVoice = voices.find(v => v.name && v.name.includes(preferred));
                if (chosenVoice) break;
            }}

            if (!chosenVoice) {{
                chosenVoice = voices.find(v => v.lang && v.lang.startsWith("en"));
            }}

            if (chosenVoice) {{
                utterance.voice = chosenVoice;
            }}

            synth.cancel();
            synth.speak(utterance);
        }}

        if (synth.getVoices().length === 0) {{
            synth.onvoiceschanged = speakNow;
        }} else {{
            speakNow();
        }}
    }})();
    </script>
    """
    components.html(js_code, height=0)
def play_jayden_talking(frame_holder, text=None):
    frames = [
        "jayden_idle.png",
        "jayden_talk_1.png",
        "jayden_talk_2.png",
        "jayden_talk_3.png",
        "jayden_talk_2.png",
        "jayden_talk_1.png",
        "jayden_idle.png"
    ]

    # Show the mouth movement first so it's obvious
    for _ in range(3):
        for frame in frames:
            frame_holder.image(frame, width=620)
            time.sleep(0.35)

    frame_holder.image("jayden_idle.png", width=620)

    if text:
        speak_text(text)

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
    except Exception:
        return "I had trouble understanding that recording."

def render_splash_video_with_balloons(video_path: str):
    try:
        with open(video_path, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error("Video not found")
        return

    html = f"""
    <div class="splash-scene">
        <video class="splash-video" controls autoplay playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
            Your browser does not support the video tag.
        </video>

        <div class="splash-bg">
            <div class="splash-balloon sb1"></div>
            <div class="splash-balloon sb2"></div>
            <div class="splash-balloon sb3"></div>
            <div class="splash-balloon sb4"></div>
            <div class="splash-balloon sb5"></div>
            <div class="splash-balloon sb6"></div>
        </div>
    </div>
    """

    components.html(html, height=520)

def interpret_child_message(text: str):
    lowered = text.lower().strip()

    if any(phrase in lowered for phrase in ["i am happy", "i'm happy", "happy", "good", "excited", "great"]):
        return "I’m so glad you feel happy. That makes me smile."

    if any(phrase in lowered for phrase in ["i am sad", "i'm sad", "sad", "crying", "unhappy", "upset"]):
        return "It’s okay to feel sad. I’m here with you. Let’s take a slow breath together."

    if any(phrase in lowered for phrase in ["i am angry", "i'm angry", "angry", "mad", "frustrated"]):
        return "I see you’re feeling angry. That’s okay. Let’s pause and take a deep breath together."

    if any(phrase in lowered for phrase in ["i am scared", "i'm scared", "scared", "afraid", "nervous", "worried"]):
        return "You are safe right now. I’m here with you. Let’s take a calm breath together."

    if any(phrase in lowered for phrase in ["i need help", "help me", "can you help", "help"]):
        return "I can help you. Let’s take one small step together."

    if any(phrase in lowered for phrase in ["i need a break", "break", "too much", "too loud", "i want a break"]):
        return "It is okay to take a break. Let’s breathe and rest for a moment."

    if any(phrase in lowered for phrase in ["hello", "hi", "hey"]):
        return "Hello, friend. I’m happy to talk with you."

    if any(phrase in lowered for phrase in ["i am okay", "i'm okay", "okay", "fine"]):
        return "I’m glad you told me. Thank you for checking in with me."

    return "Thank you for telling me. I am here with you."


def get_response(emotion: str):
    responses = {
        "happy": "I’m so glad you feel happy. That makes me smile.",
        "sad": "It’s okay to feel sad. I’m here with you. Let’s take a slow breath together.",
        "angry": "I see you’re feeling angry. That’s okay. Let’s pause and take a deep breath together.",
        "scared": "You are safe right now. I’m here with you. Let’s take a calm breath together."
    }
    return responses.get(emotion, "I’m here to help you. You’re doing a great job.")


def go(screen_name: str):
    st.session_state.screen = screen_name


def select_emotion(emotion: str):
    st.session_state.selected_emotion = emotion_map[emotion]
    go("response")


def speak_phrase(phrase: str):
    st.session_state.last_spoken_phrase = phrase
    speak_text(phrase)


def start_splash():
    st.session_state.splash_started = True
    speak_text("Hi friend. I’m Jayden. Let’s have a calm day together.")


def render_jayden_bike_intro(avatar_base64=None):
    if avatar_base64:
        avatar_html = (
            f'<div class="jayden-avatar-wrap">'
            f'  <img src="data:image/png;base64,{avatar_base64}" class="jayden-avatar" />'
            f'  <div class="jayden-wave">👋</div>'
            f'</div>'
        )
    else:
        avatar_html = (
            '<div class="jayden-avatar-wrap">'
            '  <div class="jayden-avatar jayden-fallback-avatar">🎈</div>'
            '  <div class="jayden-wave">👋</div>'
            '</div>'
        )

    html = f"""
    <div class="jayden-stage">
        <div class="jayden-ground"></div>
        <div class="jayden-rider">
            {avatar_html}
            <div class="bike">
                <div class="wheel left"></div>
                <div class="wheel right"></div>
                <div class="bike-frame">
                    <div class="handlebar"></div>
                    <div class="seat"></div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# --------------------------------------------------
# Styles
# --------------------------------------------------
st.markdown("""
<style>
.splash-scene {
    position: relative;
    width: 100%;
    max-width: 760px;
    margin: 0 auto 1rem auto;
    height: 500px;
    overflow: hidden;
    border-radius: 24px;
}

.splash-video {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
    border-radius: 24px;
    background: transparent;
}

.splash-bg {
    position: absolute;
    inset: 0;
    z-index: 3;
    pointer-events: none;
    overflow: hidden;
}

.splash-balloon {
    position: absolute;
    bottom: -150px;
    width: 10px;
    height: 130px;
    border-radius: 50% 50% 45% 45%;
    opacity: 0.38;
    animation: floatUp linear infinite;
    filter: blur(0.2px);
}

.splash-balloon::after {
    content: "";
    position: absolute;
    left: 50%;
    top: 105px;
    width: 2px;
    height: 75px;
    background: rgba(120,140,160,0.22);
    transform: translateX(-50%);
}

.sb1 { left: 3%;  background: #8fd3ff; animation-duration: 20s; }
.sb2 { left: 16%; background: #ffd8e8; animation-duration: 24s; }
.sb3 { left: 30%; background: #ffe49f; animation-duration: 22s; }
.sb4 { left: 46%; background: #bde7c8; animation-duration: 26s; }
.sb5 { left: 64%; background: #cfc8ff; animation-duration: 21s; }
.sb6 { left: 82%; background: #ffcfb3; animation-duration: 25s; }

@keyframes floatUp {
    0%   { transform: translateY(0) translateX(0px); opacity: 0; }
    10%  { opacity: 0.22; }
    50%  { transform: translateY(-52vh) translateX(12px); }
    100% { transform: translateY(-120vh) translateX(-10px); opacity: 0; }
}

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

.app-brand {
    font-size: 2rem;
    font-weight: 800;
    color: #17384b;
    margin-bottom: 0.15rem;
    letter-spacing: -0.02em;
}

.app-subbrand {
    font-size: 1rem;
    font-weight: 600;
    color: #4b6f82;
    margin-bottom: 0.25rem;
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

[data-testid="stAudioInput"] {
    background: rgba(255,255,255,0.9);
    border-radius: 20px;
    padding: 0.4rem;
}

[data-testid="stSuccess"],
[data-testid="stInfo"] {
    border-radius: 18px;
}

/* Splash */
.splash-wrap {
    text-align: center;
    padding: 2rem 1.5rem 1rem;
}

.splash-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #17384b;
    margin-bottom: 0.25rem;
}

.splash-subtitle {
    font-size: 1.05rem;
    font-weight: 600;
    color: #4b6f82;
    margin-bottom: 0.4rem;
}

.splash-caption {
    color: #6a8998;
    font-size: 1rem;
    margin-bottom: 1rem;
}

.splash-avatar-wrap {
    position: relative;
    display: inline-block;
    margin: 0.5rem 0 1rem 0;
}

.splash-avatar {
    width: 220px;
    height: auto;
    object-fit: contain;
    border-radius: 0;
    border: none;
    box-shadow: none;
    background: transparent;
}

.splash-wave {
    position: absolute;
    top: -4px;
    right: -8px;
    font-size: 2.2rem;
    transform-origin: 30% 70%;
    animation: splashWave 1.2s ease-in-out infinite;
}

.splash-card {
    background: linear-gradient(135deg, #d8eefb 0%, #eef8ff 100%);
    border-radius: 24px;
    padding: 1rem;
    margin: 0 auto 1rem auto;
    max-width: 560px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}

@keyframes splashWave {
    0%, 100% { transform: rotate(0deg); }
    25%      { transform: rotate(18deg); }
    50%      { transform: rotate(-10deg); }
    75%      { transform: rotate(18deg); }
}

/* Home bike animation */
.jayden-stage {
    position: relative;
    height: 190px;
    margin-bottom: 1rem;
    overflow: hidden;
}

.jayden-ground {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 28px;
    height: 6px;
    background: linear-gradient(90deg, rgba(180,220,240,0.2), rgba(120,190,220,0.45), rgba(180,220,240,0.2));
    border-radius: 999px;
}

.jayden-rider {
    position: absolute;
    bottom: 20px;
    left: -180px;
    display: flex;
    align-items: center;
    gap: 10px;
    animation:
        rideIn 4.6s ease-out 0.2s forwards,
        gentleBob 2.2s ease-in-out 4.9s infinite;
}

.jayden-avatar-wrap {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.jayden-avatar {
    width: 180px;
    height: auto;
    object-fit: contain;
    border-radius: 0;
    border: none;
    box-shadow: none;
    background: transparent;
    animation: peekForward 7s ease-in-out 6s infinite;
    transform-origin: center center;
}
            
.jayden-fallback-avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.2rem;
}

.jayden-wave {
    position: absolute;
    top: -6px;
    right: -8px;
    font-size: 1.8rem;
    transform-origin: 30% 70%;
    animation:
        waveHello 1.2s ease-in-out 4.9s 3,
        waveIdle 10s ease-in-out 10s infinite;
}

.bike {
    position: relative;
    width: 90px;
    height: 52px;
}

.wheel {
    position: absolute;
    bottom: 0;
    width: 28px;
    height: 28px;
    border: 4px solid #5fa9cc;
    border-radius: 50%;
    background: rgba(255,255,255,0.85);
    animation: spinWheel 0.8s linear infinite;
}

.wheel.left { left: 0; }
.wheel.right { right: 0; }

.bike-frame {
    position: absolute;
    left: 18px;
    top: 10px;
    width: 54px;
    height: 24px;
}

.bike-frame::before,
.bike-frame::after {
    content: "";
    position: absolute;
    background: #6bb7da;
    border-radius: 999px;
}

.bike-frame::before {
    width: 44px;
    height: 4px;
    top: 8px;
    left: 4px;
    transform: rotate(-12deg);
}

.bike-frame::after {
    width: 24px;
    height: 4px;
    top: 14px;
    left: 16px;
    transform: rotate(35deg);
}

.handlebar,
.seat {
    position: absolute;
    background: #4b6f82;
    border-radius: 999px;
}

.handlebar {
    width: 12px;
    height: 4px;
    top: 4px;
    right: 12px;
    transform: rotate(-18deg);
}

.seat {
    width: 12px;
    height: 4px;
    top: 6px;
    left: 10px;
}

@keyframes rideIn {
    0%   { left: -180px; }
    65%  { left: 52%; transform: translateX(-50%); }
    100% { left: 62%; transform: translateX(-50%); }
}

@keyframes gentleBob {
    0%, 100% { transform: translateX(-50%) translateY(0px); }
    50%      { transform: translateX(-50%) translateY(-3px); }
}

@keyframes peekForward {
    0%, 72%, 100% { transform: scale(1) translateX(0px); }
    78%           { transform: scale(1.08) translateX(10px); }
    84%           { transform: scale(1.02) translateX(4px); }
}

@keyframes spinWheel {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

@keyframes waveHello {
    0%, 100% { transform: rotate(0deg); }
    25%      { transform: rotate(18deg); }
    50%      { transform: rotate(-10deg); }
    75%      { transform: rotate(18deg); }
}

@keyframes waveIdle {
    0%, 94%, 100% { transform: rotate(0deg); }
    95%           { transform: rotate(16deg); }
    96%           { transform: rotate(-8deg); }
    97%           { transform: rotate(14deg); }
    98%           { transform: rotate(0deg); }
}
/* 🎈 Splash balloons behind video */
/* 🎈 Splash balloons in front of video */
.splash-scene {
    position: relative;
    width: 100%;
    margin-bottom: 1rem;
}

.splash-video-wrap {
    position: relative;
    z-index: 1;
    border-radius: 24px;
    overflow: hidden;
}

.splash-bg {
    position: absolute;
    inset: 0;
    z-index: 3;
    pointer-events: none;
    overflow: hidden;
}

.splash-balloon {
    position: absolute;
    bottom: -150px;
    width: 90px;
    height: 110px;
    border-radius: 50% 50% 45% 45%;
    opacity: 0.28;
    animation: floatUp linear infinite;
}

.splash-balloon::after {
    content: "";
    position: absolute;
    left: 50%;
    top: 95px;
    width: 2px;
    height: 70px;
    background: rgba(120,140,160,0.25);
    transform: translateX(-50%);
}

.sb1 { left: 5%;  background: #8fd3ff; animation-duration: 20s; }
.sb2 { left: 18%; background: #ffd8e8; animation-duration: 24s; }
.sb3 { left: 32%; background: #ffe49f; animation-duration: 22s; }
.sb4 { left: 50%; background: #bde7c8; animation-duration: 26s; }
.sb5 { left: 70%; background: #cfc8ff; animation-duration: 21s; }
.sb6 { left: 85%; background: #ffcfb3; animation-duration: 25s; }
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
# Session state
# --------------------------------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "home"

if "show_splash" not in st.session_state:
    st.session_state.show_splash = True

if "splash_started" not in st.session_state:
    st.session_state.splash_started = False

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
# Avatar/header
# --------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
AVATAR_FILE = os.path.join(APP_DIR, "jayden_avatar.png")
avatar_base64 = get_base64_image(AVATAR_FILE)

title_col, avatar_col = st.columns([1, 0.01])

with title_col:
    st.markdown("<div class='app-brand'>🎈 Jayden’s Calm Journey</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-subbrand'>Autism Support Chatbot</div>", unsafe_allow_html=True)

with avatar_col:
    st.empty()

st.markdown(
    "<div class='app-caption'>A gentle space to help children feel calm, safe, and understood.</div>",
    unsafe_allow_html=True
)# --------------------------------------------------
# Splash screen
# --------------------------------------------------
st.markdown("""
<div class="splash-bg">
    <div class="splash-balloon sb1"></div>
    <div class="splash-balloon sb2"></div>
    <div class="splash-balloon sb3"></div>
    <div class="splash-balloon sb4"></div>
    <div class="splash-balloon sb5"></div>
    <div class="splash-balloon sb6"></div>
</div>
""", unsafe_allow_html=True)
# --------------------------------------------------
# Splash screen (Video Intro)
# --------------------------------------------------
if st.session_state.show_splash:
    video_path = os.path.join(os.getcwd(), "jayden_intro.mp4")
    render_splash_video_with_balloons(video_path)

    if st.button("🌈 Start My Calm Journey", use_container_width=True):
        st.session_state.show_splash = False
        st.rerun()

    st.stop()
# --------------------------------------------------
# Screen router
# --------------------------------------------------
screen = st.session_state.screen

if st.button("🔊 Test Voice Output"):
    speak_text("Hello, friend. I am here to help you.")
    st.success("Voice test triggered.")


# --------------------------------------------------
# Home
# --------------------------------------------------
if screen == "home":

    if st.button("Test Voice Only"):
        speak_text("Hi friend, I’m Jayden.")
    
    render_jayden_bike_intro(avatar_base64)

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

    if st.button("💬 Talk with Jayden", use_container_width=True):
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
    response_text = f"{selected['heading']} {selected['body']}"

    st.markdown(f"""
    <div class='soft-card'>
        <div class='card-title'>{selected['emoji']} {selected['heading']}</div>
        <div class='card-text'>{selected['body']}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔊 Speak", use_container_width=True):
        speak_text(response_text)

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
        st.markdown(
            f"<div class='soft-card'><div class='card-text'>{step}</div></div>",
            unsafe_allow_html=True
        )

    if st.button("➡ Next Step", use_container_width=True):
        st.success("Great job. Keep going.")

    if st.button("🔊 Say Encouragement", use_container_width=True):
        speak_text("Great job. Keep going.")

    if st.button("🏠 Home", use_container_width=True):
        go("home")


# --------------------------------------------------
# Talk with Jayden
# --------------------------------------------------
elif screen == "talking":
    st.markdown("""
    <div class='soft-card'>
        <div class='card-title'>💬 Talk with Jayden</div>
        <div class='card-text'>Let’s practice simple words together.</div>
    </div>
    """, unsafe_allow_html=True)

    jayden_frame = st.empty()
    jayden_frame.image("jayden_idle.png", width=620)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👋 Hello", use_container_width=True):
            st.success("Nice job saying hello.")
            play_jayden_talking(jayden_frame, "Nice job saying hello.")

    with col2:
        if st.button("🙂 Hi", use_container_width=True):
            st.success("Great greeting.")
            play_jayden_talking(jayden_frame, "Great greeting.")

    if st.button("🧪 Test Mouth Frames", use_container_width=True):
        for frame in [
            "jayden_idle.png",
            "jayden_talk_1.png",
            "jayden_talk_2.png",
            "jayden_talk_3.png",
            "jayden_talk_2.png",
            "jayden_talk_1.png",
            "jayden_idle.png"
        ]:
            jayden_frame.image(frame, width=620)
            time.sleep(1.0)

    if st.button("🔁 Try Again", use_container_width=True):
        st.info("Let’s practice again.")
        play_jayden_talking(jayden_frame, "Let’s practice again. Say hello.")

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

            response = interpret_child_message(text)
            st.success(response)
            play_jayden_talking(jayden_frame, response)

    if st.button("🏠 Home", use_container_width=True):
        go("home")