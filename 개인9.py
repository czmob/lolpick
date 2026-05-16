from playwright.sync_api import sync_playwright
import pandas as pd
import numpy as np

def crawl(riot_id):
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://op.gg/ko/lol/summoners/kr/{riot_id.replace('#','-')}/champions"
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        rows = page.locator("td.text-xs.bg-gray-100")

        for i in range(rows.count()):
            try:
                row = rows.nth(i).locator("xpath=ancestor::tr")
                text = row.inner_text()

                img = row.locator("img").first
                champ = img.get_attribute("alt")
                if not champ:
                    continue

                win = len([x for x in text.split() if "승" in x])
                loss = len([x for x in text.split() if "패" in x])

                games = win + loss
                if games == 0:
                    continue

                winrate = win / games * 100

                data.append({
                    "champ": champ,
                    "games": games,
                    "winrate": winrate,
                    "kda": 2.0
                })

            except:
                continue

        browser.close()

    df = pd.DataFrame(data)

    if df.empty:
        return df

    df["score"] = (
        df["games"] * 0.3 +
        df["winrate"] * 0.2 +
        df["kda"] * 0.5
    )

    return df
