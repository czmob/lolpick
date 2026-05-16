from playwright.sync_api import sync_playwright
import pandas as pd
import re
import time
import traceback

# ==========================================
# 탑 챔피언 리스트 (53개)
# ==========================================
TOP_CHAMPIONS = [
    "Aatrox", "Akali", "Camille", "Cho'Gath", "Darius", "Dr. Mundo",
    "Fiora", "Gangplank", "Garen", "Gnar", "Gragas", "Gwen",
    "Illaoi", "Irelia", "Jax", "Jayce", "K'Sante", "Kayle",
    "Kennen", "Kled", "Malphite", "Mordekaiser", "Nasus", "Olaf",
    "Ornn", "Pantheon", "Poppy", "Quinn", "Renekton", "Riven",
    "Rumble", "Sett", "Shen", "Singed", "Sion", "Sylas",
    "Tahm Kench", "Teemo", "Trundle", "Tryndamere", "Urgot",
    "Vayne", "Volibear", "Wukong", "Yorick", "Yone", "Yasuo",
    "Heimerdinger", "Akshan", "Warwick", "Zac", "Shaco", "Briar"
]

# ==========================================
# 챔피언 이름 -> OP.GG slug
# ==========================================
def slug(name):
    special = {
        "Cho'Gath": "chogath",
        "Dr. Mundo": "drmundo",
        "K'Sante": "ksante",
        "Tahm Kench": "tahmkench",
        "Wukong": "monkeyking",
        "Kai'Sa": "kaisa",
        "Bel'Veth": "belveth",
    }

    if name in special:
        return special[name]

    return (
        name.lower()
        .replace(" ", "")
        .replace(".", "")
        .replace("'", "")
    )

# ==========================================
# URL 생성
# ==========================================
def build_url(enemy, champ):
    return (
        f"https://www.op.gg/lol/champions/"
        f"{slug(enemy)}/counters/top"
        f"?target_champion={slug(champ)}"
        f"&sort_type=play"
        f"&sort_direction=-1"
    )

# ==========================================
# Lane Kill Rate 추출
# - 보라색 값이 있으면 그대로 사용
# - 없으면 첫 번째 퍼센트를 읽고 100 - 값
# ==========================================
def extract_lane_kill(page):
    try:
        # 1) 보라색 강조값 탐색
        selector = "span.absolute.bottom-3.right-0.font-bold.text-purple-500"
        elements = page.locator(selector)

        if elements.count() > 0:
            text = elements.first.inner_text().strip()
            match = re.search(r"(\d+(?:\.\d+)?)%", text)

            if match:
                value = float(match.group(1))
                if 30 <= value <= 75:
                    return value

        # 2) body 전체에서 퍼센트 찾기
        body = page.locator("body").inner_text()
        matches = re.findall(r"(\d+(?:\.\d+)?)%", body)

        for value in matches:
            v = float(value)

            # Lane Kill Rate로 가능한 범위
            if 30 <= v <= 75:
                return round(100 - v, 2)

        return None

    except Exception:
        return None

# ==========================================
# HTTP 429 감지
# ==========================================
def is_rate_limited(page):
    try:
        title = page.title()
        body = page.locator("body").inner_text()

        return (
            "429" in title
            or "Too Many Requests" in body
            or "HTTP ERROR 429" in body
        )
    except Exception:
        return False

# ==========================================
# 메인 실행
# ==========================================
def run(enemy):
    results = []

    candidates = [
        champ for champ in TOP_CHAMPIONS
        if champ.lower() != enemy.lower()
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        total = len(candidates)

        for i, champ in enumerate(candidates, start=1):
            url = build_url(enemy, champ)

            print(f"{i}/{total} {champ} vs {enemy}")
            print("🌐", url)

            rate = None

            for attempt in range(3):
                try:
                    page.goto(url, wait_until="domcontentloaded")
                    page.wait_for_timeout(3000)

                    # 429 차단 감지
                    if is_rate_limited(page):
                        print("⏳ HTTP 429 감지 → 60초 대기")
                        time.sleep(60)
                        continue

                    rate = extract_lane_kill(page)

                    if rate is not None:
                        break

                except Exception:
                    pass

                time.sleep(5)

            print(f"   → {rate}")

            results.append({
                "enemy": enemy,
                "champion": champ,
                "lane_kill_rate": rate
            })

            # 요청 간격
            time.sleep(2)

        browser.close()

    # DataFrame 생성
    df = pd.DataFrame(results)

    # None 제거
    df = df.dropna(subset=["lane_kill_rate"])

    # 데이터 없으면 빈 CSV 저장
    if df.empty:
        print("\n❌ 추출된 데이터가 없습니다.")
        filename = f"{enemy}_lane_kill.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"💾 빈 CSV 저장 완료: {filename}")
        return

    # 정렬
    df = df.sort_values(
        by="lane_kill_rate",
        ascending=False
    ).reset_index(drop=True)

    # 결과 출력
    print("\n🔥 TOP 10")
    print(df.head(10))

    # CSV 저장
    filename = f"{enemy}_lane_kill.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"\n💾 CSV 저장 완료: {filename}")
    print(f"총 {len(df)}개 챔피언 데이터 저장")

# ==========================================
# 실행
# ==========================================
if __name__ == "__main__":
    try:
        enemy = input("상대 챔피언 입력: ").strip()
        run(enemy)

    except Exception as e:
        print("\n❌ 오류 발생:")
        print(type(e).__name__, "-", e)
        print()
        traceback.print_exc()

    finally:
        input("\n엔터 누르면 종료")
