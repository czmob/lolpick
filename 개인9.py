import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def crawl(riot_id):

    data = []

    # Riot ID 변환
    safe_id = riot_id.replace("#", "-")

    url = f"https://op.gg/ko/lol/summoners/kr/{safe_id}/champions"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }

    # 요청
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("❌ 요청 실패:", response.status_code)
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "lxml")

    # 모든 row 탐색
    rows = soup.find_all("tr")

    for row in rows:

        try:
            text = row.get_text(" ", strip=True)

            # 승/패 없는 행 제거
            if "승" not in text or "패" not in text:
                continue

            # 챔피언 이미지 alt 추출
            img = row.find("img")

            if not img:
                continue

            champ = img.get("alt")

            if not champ:
                continue

            # 승/패 추출
            win = 0
            loss = 0

            parts = text.split()

            for part in parts:

                if "승" in part:
                    try:
                        win = int(part.replace("승", ""))
                    except:
                        pass

                if "패" in part:
                    try:
                        loss = int(part.replace("패", ""))
                    except:
                        pass

            games = win + loss

            if games == 0:
                continue

            winrate = round(win / games * 100, 2)

            # 임시 KDA
            kda = 2.0

            data.append({
                "champ": champ,
                "games": games,
                "winrate": winrate,
                "kda": kda
            })

            print(champ, games, winrate)

        except Exception as e:
            print("ROW ERROR:", e)
            continue

    # DataFrame
    df = pd.DataFrame(data)

    if df.empty:
        print("❌ 데이터 없음")
        return df

    # 점수 계산
    df["score"] = (
        df["games"] * 0.3 +
        df["winrate"] * 0.2 +
        df["kda"] * 0.5
    )

    # 정렬
    df = df.sort_values(
        by="score",
        ascending=False
    ).reset_index(drop=True)

    # 저장
    df.to_csv(
        "opgg_mastery_final.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("💾 저장 완료")

    return df
