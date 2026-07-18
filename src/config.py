import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    try:
        import streamlit as st
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if not GEMINI_API_KEY:
    print("[WARNING]: API Key is missing. Check your .env file or Streamlit secrets!")