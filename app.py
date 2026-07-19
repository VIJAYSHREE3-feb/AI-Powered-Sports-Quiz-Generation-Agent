import streamlit as st
from src.generator import compile_quiz_data
from src.database import setup_and_populate_db


# 1. Warm-up and initialize the vector DB with our offline facts on startup
@st.cache_resource
def prepare_knowledge_base():
    setup_and_populate_db()


prepare_knowledge_base()

# 2. Set Page configurations
st.set_page_config(page_title="Sports Quiz Agent", page_icon="🏆", layout="centered")

import base64

# 2b. Sport -> background image mapping. Each image is a pre-composited
# "banner" (1920x1080): the full original poster shown sharp and uncropped,
# centered, with a blurred/darkened copy of the same image filling the rest
# of the frame edge-to-edge. This gives a true full-screen background with
# nothing ever cropped or cut off, on any screen size.
SPORT_BACKGROUNDS = {
    "Cricket": "assets/backgrounds/cricket_banner.jpg",
    "Football": "assets/backgrounds/football_banner.jpg",
    "Badminton": "assets/backgrounds/badminton_banner.jpg",
    "Tennis": "assets/backgrounds/tennis_banner.jpg",
    "Basketball": "assets/backgrounds/basketball_banner.jpg",
    "Hockey": "assets/backgrounds/hockey_banner.jpg",
    "Formula 1": "assets/backgrounds/formula1_banner.jpg",
    "Athletics": "assets/backgrounds/athletics_banner.jpg",
}


@st.cache_data
def get_base64_image(local_path):
    """Reads a local image file and returns it as a base64 data URI string."""
    with open(local_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/jpg;base64,{encoded}"


def apply_sport_background(sport_name):
    """Injects CSS to change the app's (and sidebar's) background image based on selected sport."""
    local_path = SPORT_BACKGROUNDS.get(sport_name)
    if not local_path:
        return
    try:
        image_url = get_base64_image(local_path)
    except FileNotFoundError:
        return  # Silently skip if the image file is missing, rather than crash the app
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stSidebar"] {{
            background: rgba(14, 17, 23, 0.55);
            backdrop-filter: blur(6px);
        }}
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}
        @media (max-width: 768px) {{
            [data-testid="stAppViewContainer"] {{
                background-attachment: scroll;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


st.title("🏆 AI-Powered Sports Quiz Generator")
st.write("Challenge yourself or generate engaging social media content! Powered by RAG (ChromaDB + Web Search).")

# 3. Sidebar inputs
st.sidebar.header("Quiz Settings")
sport_choice = st.sidebar.selectbox(
    "Select Sport",
    ["Cricket", "Football", "Badminton", "Tennis", "Basketball", "Hockey", "Formula 1", "Athletics"]
)
difficulty = st.sidebar.select_slider("Select Difficulty", options=["Easy", "Medium", "Hard"])

# Apply the themed background for whichever sport is currently selected —
# updates live as soon as the dropdown changes, even before generating a quiz.
apply_sport_background(sport_choice)

# 4. Initialize session state to remember quizzes across page interactions
if "quiz_output" not in st.session_state:
    st.session_state.quiz_output = None
    st.session_state.quiz_context = None

# Button to trigger compilation pipeline
if st.sidebar.button("Generate Fresh Quiz", use_container_width=True):
    with st.spinner("Fetching historical facts & scouring the live web..."):
        try:
            quiz_text, context_used = compile_quiz_data(sport_choice, difficulty)
            st.session_state.quiz_output = quiz_text
            st.session_state.quiz_context = context_used
            st.success("Quiz created successfully!")
        except Exception as e:
            st.error(f"Failed to generate quiz: {e}")

# 5. Display the generated quiz
if st.session_state.quiz_output:
    st.subheader(f"Current Quiz: {sport_choice} ({difficulty})")
    st.text_area("Generated Quiz Output (Copy paste to your socials)",
                 value=st.session_state.quiz_output,
                 height=350)

    # Expandable window showcasing the "ground truth context" for audit purposes
    with st.expander("🔍 Inspect Ground Truth (RAG Context Used)"):
        st.code(st.session_state.quiz_context, language="markdown")
