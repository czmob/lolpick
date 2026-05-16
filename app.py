import pandas as pd
from 기린다 import run as lane_run
from 개인9 import crawl as mastery_run


def normalize(x):
    return x.lower().replace(" ", "").replace(".", "").replace("'", "")


def main():
    enemy = input("상대 챔피언: ").strip()
    riot_id = input("Riot ID: ").strip()

    print("\n[1/3] lane 크롤링")
    lane_df = lane_run(enemy)

    print("\n[2/3] 숙련도 크롤링")
    mastery_df = mastery_run(riot_id)

    if lane_df.empty or mastery_df.empty:
        print("❌ 데이터 없음")
        return

    lane_df["champ"] = lane_df["champ"].apply(normalize)
    mastery_df["champ"] = mastery_df["champ"].apply(normalize)

    df = pd.merge(mastery_df, lane_df, on="champ", how="inner")

    if df.empty:
        print("❌ merge 실패")
        return

    def norm(x):
        return (x - x.min()) / (x.max() - x.min() + 1e-9)

    df["pick_score"] = (
        norm(df["score"]) * 0.55 +
        norm(df["lane_kill_rate"]) * 0.45
    )

    df = df.sort_values("pick_score", ascending=False)

    print("\n🔥 TOP PICKS")
    print(df[["champ", "pick_score"]].head(10))


if __name__ == "__main__":
    main()
    
