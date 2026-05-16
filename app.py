import streamlit as st

st.title("🎮 LoL Pick Recommender")

enemy = st.text_input("상대 챔피언")
riot_id = st.text_input("내 Riot ID (예: Hide on bush#KR1)")

if st.button("추천 시작"):
    st.write(f"상대 챔피언: {enemy}")
    st.write(f"Riot ID: {riot_id}")
    st.success("여기에 추천 결과가 표시됩니다.")
