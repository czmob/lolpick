import streamlit as st
from 기린다 import run as lane_run
from 개인9 import crawl as mastery_run

st.title("🎮 LoL Pick Recommender")

# ✅ session_state 기반 고정
if "enemy" not in st.session_state:
    st.session_state.enemy = ""

if "riot_id" not in st.session_state:
    st.session_state.riot_id = ""

st.session_state.enemy = st.text_input("상대 챔피언", value=st.session_state.enemy)
st.session_state.riot_id = st.text_input("Riot ID (name#kr1)", value=st.session_state.riot_id)

if st.button("추천 시작"):

    enemy = st.session_state.enemy.strip()
    riot_id = st.session_state.riot_id.strip()

    if enemy == "" or riot_id == "":
        st.warning("입력하세요")
        st.stop()

    st.write("크롤링 중...")

    lane_df = lane_run(enemy)
    mastery_df = mastery_run(riot_id)

    st.success("완료!")

    st.dataframe(lane_df)
    st.dataframe(mastery_df)
