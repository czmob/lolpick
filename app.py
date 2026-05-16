import streamlit as st
from 기린다 import run as lane_run
from 개인9 import crawl as mastery_run

st.title("🎮 LoL Pick Recommender")

# 상태 저장
if "enemy" not in st.session_state:
    st.session_state.enemy = ""

if "riot_id" not in st.session_state:
    st.session_state.riot_id = ""

# 입력 (항상 state에 저장)
st.session_state.enemy = st.text_input("상대 챔피언", st.session_state.enemy)
st.session_state.riot_id = st.text_input("Riot ID (name#kr1)", st.session_state.riot_id)

# 버튼
if st.button("추천 시작"):

    enemy = st.session_state.enemy.strip()
    riot_id = st.session_state.riot_id.strip()

    # 🔥 여기 중요 (print로 확인)
    st.write("DEBUG:", enemy, riot_id)

    if enemy == "" or riot_id == "":
        st.warning("입력하세요")
        st.stop()

    st.write("크롤링 중...")

    lane_df = lane_run(enemy)
    mastery_df = mastery_run(riot_id)

    st.success("완료")

    st.dataframe(lane_df)
