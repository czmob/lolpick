import streamlit as st
import subprocess
import sys

st.title("🎮 LoL Pick Recommender")

enemy = st.text_input("상대 챔피언")
riot_id = st.text_input("내 Riot ID (예: Hide on bush#KR1)")

if st.button("추천 시작"):
    result = subprocess.run(
        [sys.executable, "가봅시다.py"],
        input=f"{enemy}\n{riot_id}\n",
        text=True,
        capture_output=True
    )

    st.text(result.stdout)

    if result.stderr:
        st.error(result.stderr)
