import streamlit as st
from src.generator import compile_quiz_data
from src.database import setup_and_populate_db


# 1. Warm-up and initialize the vector DB with our offline facts on startup
@st.cache_resource
def prepare_knowledge_base():
    setup_and_populate_db()


prepare_knowledge_base()

# 2. Set Page configurations. "wide" gives enough room for a clean
# image-on-one-side / quiz-on-the-other layout.
st.set_page_config(page_title="Sports Quiz Agent", page_icon="🏆", layout="wide")

# 2b. Sport -> image mapping. These are the original, uncropped posters —
# shown as a normal image in a dedicated column, not as a background, so
# text always stays fully readable regardless of the image's busyness.
SPORT_IMAGES = {
    "Cricket": "assets/backgrounds/cricket.jpg",
    "Football": "assets/backgrounds/football.jpg",
    "Badminton": "assets/backgrounds/badminton.jpg",
    "Tennis": "assets/backgrounds/tennis.jpg",
    "Basketball": "assets/backgrounds/basketball.jpg",
    "Hockey": "assets/backgrounds/hockey.jpg",
    "Formula 1": "assets/backgrounds/formula1.jpg",
    "Athletics": "assets/backgrounds/athletics.jpg",
}

# 3. Sidebar inputs (settings live here regardless of layout)
st.sidebar.header("Quiz Settings")
sport_choice = st.sidebar.selectbox(
    "Select Sport",
    ["Cricket", "Football", "Badminton", "Tennis", "Basketball", "Hockey", "Formula 1", "Athletics"]
)
difficulty = st.sidebar.select_slider("Select Difficulty", options=["Easy", "Medium", "Hard"])

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

# 5. Main layout: image on the left, everything else on the right.
# This keeps all text on a plain background — always readable — while
# still giving each sport its own visual identity via the side image.
img_col, content_col = st.columns([1, 1.4], gap="large")

with img_col:
    image_path = SPORT_IMAGES.get(sport_choice)
    if image_path:
        st.image(image_path, use_container_width=True, caption=sport_choice)

with content_col:
    st.title("🏆 AI-Powered Sports Quiz Generator")
    st.write("Challenge yourself or generate engaging social media content! Powered by RAG (ChromaDB + Web Search).")

    if st.session_state.quiz_output:
        st.subheader(f"Current Quiz: {sport_choice} ({difficulty})")
        st.text_area("Generated Quiz Output (Copy paste to your socials)",
                     value=st.session_state.quiz_output,
                     height=350)

        # Expandable window showcasing the "ground truth context" for audit purposes
        with st.expander("🔍 Inspect Ground Truth (RAG Context Used)"):
            st.code(st.session_state.quiz_context, language="markdown")
    else:
        st.info("👈 Pick a sport and difficulty in the sidebar, then click **Generate Fresh Quiz**.")
