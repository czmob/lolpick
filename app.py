import streamlit as st
from 기린다 import run as lane_run
from 개인9 import crawl as mastery_run

st.title("🎮 LoL Pick Recommender")

enemy = st.text_input("상대 챔피언")
riot_id = st.text_input("Riot ID (name#kr1)")

if st.button("추천 시작"):
    if not enemy or not riot_id:
        st.warning("입력하세요")
        st.stop()

    st.write("크롤링 중...")

    lane_df = lane_run(enemy)
    mastery_df = mastery_run(riot_id)

    st.write("완료!")

    st.dataframe(lane_df)
    st.dataframe(mastery_df)
