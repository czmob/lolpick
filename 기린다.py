from playwright.sync_api import sync_playwright
import pandas as pd
import time
import re

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

def slug(name):
    return (
        name.lower()
        .replace(" ", "")
        .replace(".", "")
        .replace("'", "")
    )

def build_url(enemy, champ):
    return f"https://www.op.gg/lol/champions/{slug(enemy)}/counters/top?target_champion={slug(champ)}"

def extract_lane_kill(page):
    body = page.locator("body").inner_text()
    matches = re.findall(r"(\d+(?:\.\d+)?)%", body)

    for v in matches:
        v = float(v)
        if 30 <= v <= 75:
            return round(100 - v, 2)

    return None

def run(enemy):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for champ in TOP_CHAMPIONS:
            if champ.lower() == enemy.lower():
                continue

            url = build_url(enemy, champ)
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(800)

            rate = extract_lane_kill(page)

            results.append({
                "champ": champ,
                "lane_kill_rate": rate
            })

        browser.close()

    return pd.DataFrame(results)
