import os
import time
import subprocess
import pandas as pd
import numpy as np
import traceback


def pause():
    try:
        input("\n엔터 누르면 종료")
    except:
        pass


def wait_file(path, timeout=500):
    print(f"[WAIT] {path} 생성 대기 중...")

    for i in range(timeout):
        if os.path.exists(path):
            print(f"[OK] 파일 생성됨: {path}")
            return True
        time.sleep(1)
        print(f"  - {i+1}s")

    return False


try:
    # -----------------------------
    # 1. 입력 (핵심 수정)
    # -----------------------------
    enemy = input("상대 챔피언: ").strip().lower()
    riot_id = input("내 Riot ID (name#kr1): ").strip()


    # -----------------------------
    # 2. 라인킬 크롤러 실행
    # -----------------------------
    print("\n[1/3] 라인킬 크롤링 실행")

    subprocess.run(
        ["python", "기린다.py"],
        input=enemy,
        text=True
    )


    # -----------------------------
    # 3. 파일 기다리기
    # -----------------------------
    lane_file = f"{enemy}_lane_kill.csv"

    if not wait_file(lane_file, timeout=500):
        print("❌ 라인킬 파일 생성 실패")
        pause()
        exit()


    # -----------------------------
    # 4. 숙련도 크롤러 실행
    # -----------------------------
    print("\n[2/3] 숙련도 크롤링 실행")

    subprocess.run(
        ["python", "개인9.py"],
        input=riot_id,
        text=True
    )


    mastery_file = "opgg_mastery_final.csv"

    if not wait_file(mastery_file, timeout=500):
        print("❌ 숙련도 파일 생성 실패")
        pause()
        exit()


    # -----------------------------
    # 5. 데이터 로드
    # -----------------------------
    print("\n[LOAD] CSV 로딩")

    lane = pd.read_csv(lane_file)
    mastery = pd.read_csv(mastery_file)


    # -----------------------------
    # 6. 컬럼 통일
    # -----------------------------
    if "champion" in lane.columns:
        lane["champ"] = lane["champion"]
    elif "champ" not in lane.columns:
        raise Exception("lane 컬럼 오류")

    def normalize(x):
        return x.lower().replace(" ", "").replace(".", "").replace("'", "")

    lane["champ"] = lane["champ"].apply(normalize)
    mastery["champ"] = mastery["champ"].apply(normalize)


    # -----------------------------
    # 7. merge
    # -----------------------------
    print("\n[MERGE] 진행")

    df = pd.merge(mastery, lane, on="champ", how="inner")

    print("[DEBUG] merge rows:", len(df))

    if df.empty:
        print("\n❌ MERGE 실패 (챔피언 이름 불일치)")
        pause()
        exit()


    # -----------------------------
    # 8. 점수 계산
    # -----------------------------
    def norm(x):
        return (x - x.min()) / (x.max() - x.min() + 1e-9)

    df["mastery_n"] = norm(df["score"])
    df["lane_n"] = norm(df["lane_kill_rate"])

    df["pick_score"] = (
        df["mastery_n"] * 0.55 +
        df["lane_n"] * 0.45
    )


    # -----------------------------
    # 9. 결과 출력
    # -----------------------------
    df = df.sort_values("pick_score", ascending=False)

    print("\n===== TOP PICKS =====\n")
    print(df[["champ", "pick_score"]].head(10))


    # -----------------------------
    # 10. 저장
    # -----------------------------
    out = f"{enemy}_final_pick.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")

    print(f"\n💾 저장 완료: {out}")


except Exception as e:
    print("\n🔥 ERROR 발생")
    print(type(e).__name__, "-", e)
    traceback.print_exc()

finally:
    pause()
