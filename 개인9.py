from playwright.sync_api import sync_playwright
import pandas as pd
import numpy as np
import re
from urllib.parse import quote


# -----------------------------
# 챔피언 한글 → 영어 변환
# -----------------------------
CHAMP_MAP = {
    "비에고": "Viego",
    "리 신": "LeeSin",
    "아트록스": "Aatrox",
    "벡스": "Vex",
    "야스오": "Yasuo",
    "아칼리": "Akali",
    "에코": "Ekko",
    "쓰레쉬": "Thresh",
    "파이크": "Pyke",
    "블리츠크랭크": "Blitzcrank",
    "요네": "Yone",
    "피오라": "Fiora",
    "오공": "Wukong",
    "녹턴": "Nocturne",
    "이렐리아": "Irelia",
    "아지르": "Azir",
    "블라디미르": "Vladimir",
    "이즈리얼": "Ezreal",
    "자크": "Zac",
    "마스터 이": "MasterYi",
    "바이": "Vi",
    "케인": "Kayn",
    "이블린": "Evelynn",

    # 탑 챔피언 전체
    "카밀": "Camille",
    "초가스": "ChoGath",
    "다리우스": "Darius",
    "문도 박사": "DrMundo",
    "갱플랭크": "Gangplank",
    "가렌": "Garen",
    "나르": "Gnar",
    "그라가스": "Gragas",
    "그웬": "Gwen",
    "일라오이": "Illaoi",
    "잭스": "Jax",
    "제이스": "Jayce",
    "크산테": "KSante",
    "케일": "Kayle",
    "케넨": "Kennen",
    "클레드": "Kled",
    "말파이트": "Malphite",
    "모데카이저": "Mordekaiser",
    "나서스": "Nasus",
    "올라프": "Olaf",
    "오른": "Ornn",
    "판테온": "Pantheon",
    "뽀삐": "Poppy",
    "퀸": "Quinn",
    "레넥톤": "Renekton",
    "리븐": "Riven",
    "럼블": "Rumble",
    "세트": "Sett",
    "쉔": "Shen",
    "신지드": "Singed",
    "사이온": "Sion",
    "사일러스": "Sylas",
    "탐 켄치": "TahmKench",
    "티모": "Teemo",
    "트런들": "Trundle",
    "트린다미어": "Tryndamere",
    "우르곳": "Urgot",
    "베인": "Vayne",
    "볼리베어": "Volibear",
    "요릭": "Yorick",
    "하이머딩거": "Heimerdinger",
    "아크샨": "Akshan",
    "워윅": "Warwick",
    "샤코": "Shaco",
    "브라이어": "Briar",

    # 자주 보이는 기타 챔피언
    "노틸러스": "Nautilus",
    "진": "Jhin",
    "미스 포츈": "MissFortune",
    "레오나": "Leona",
    "브라움": "Braum",
    "케이틀린": "Caitlyn",
    "갈리오": "Galio",
    "카이사": "KaiSa",
    "럭스": "Lux",
    "베이가": "Veigar",
}


# -----------------------------
# URL 생성
# -----------------------------
def build_url(riot_id):
    name, tag = riot_id.split("#")
    return f"https://op.gg/ko/lol/summoners/kr/{quote(name)}-{tag.upper()}/champions"


# -----------------------------
# 안전 추출
# -----------------------------
def get_int(text):
    m = re.search(r"(\d+)", text)
    return int(m.group(1)) if m else 0


def get_float(text):
    m = re.search(r"(\d+(\.\d+)?)", text)
    return float(m.group(1)) if m else 0.0


# -----------------------------
# row 필터
# -----------------------------
def is_valid_row(text):
    if "vs" in text:
        return False
    if "승" not in text or "패" not in text:
        return False
    if "%" not in text:
        return False
    return True


# -----------------------------
# 크롤링
# -----------------------------
def crawl(riot_id):
    url = build_url(riot_id)
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("[접속]", url)
        page.goto(url, wait_until="domcontentloaded")

        page.wait_for_timeout(5000)

        for _ in range(3):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1500)

        rows = page.locator("td.text-xs.bg-gray-100")

        print("[ROWS FOUND]", rows.count())

        for i in range(rows.count()):
            try:
                rank_td = rows.nth(i)
                row = rank_td.locator("xpath=ancestor::tr")

                text = row.inner_text()

                if not is_valid_row(text):
                    continue

                raw_champ = row.locator("img").first.get_attribute("alt")
                if not raw_champ:
                    continue

                champ = CHAMP_MAP.get(raw_champ, raw_champ)

                win = get_int(re.search(r"(\d+)\s*승", text).group())
                loss = get_int(re.search(r"(\d+)\s*패", text).group())

                games = win + loss
                if games == 0:
                    continue

                winrate = round(win / games * 100, 2)

                kda_match = re.search(r"(\d+(\.\d+)?)\s*:\s*1", text)
                kda = float(kda_match.group(1)) if kda_match else 0

                data.append({
                    "champ": champ,
                    "games": games,
                    "winrate": winrate,
                    "kda": kda
                })

                print(champ, games, winrate, kda)

            except:
                continue

        browser.close()

    return pd.DataFrame(data)


# -----------------------------
# 숙련도 계산
# -----------------------------
def make_mastery(df):
    if df.empty:
        return df

    df = df.copy()

    df["base"] = np.log2(df["games"] + 1) * np.log2(df["kda"] + 1)

    df["score"] = (
        df["base"].rank(pct=True) * 0.5 +
        df["games"].rank(pct=True) * 0.3 +
        df["winrate"].rank(pct=True) * 0.2
    )

    return df


# -----------------------------
# 실행
# -----------------------------
def run():
    riot_id = ""

    df = crawl(riot_id)

    print("\n[RESULT]", len(df))

    if df.empty:
        print("❌ 데이터 없음 (OP.GG 구조 or 로딩 문제)")
        return

    df = make_mastery(df)
    df = df.sort_values("score", ascending=False)

    print("\n===== TOP CHAMPIONS =====\n")
    print(df)

    df.to_csv("opgg_mastery_final.csv", index=False, encoding="utf-8-sig")

    print("\n💾 저장 완료: opgg_mastery_final.csv")


if __name__ == "__main__":
    run()
