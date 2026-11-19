import re
from playwright.sync_api import sync_playwright

# Initialize Playwright in synchronous mode
with sync_playwright() as p:
    # 1. Launch real Google Chrome in new headless mode to bypass Cricbuzz bot detection
    browser = p.chromium.launch(
        channel="chrome",
        headless=True,
        args=[
            "--headless=new",
            "--disable-blink-features=AutomationControlled"
        ]
    )

    # 2. Configure browser viewport and standard desktop User-Agent headers
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    # 3. Open the Cricbuzz homepage and wait for the initial HTML structure to load
    page.goto("https://cricbuzz.com", wait_until="domcontentloaded")

    # 4. Locate the BAN vs RSA match card by its URL slug and click into the live match page
    match_link = page.locator('a[href*="ban-vs-rsa"]').first
    match_link.wait_for(state="visible", timeout=20000)
    match_link.click()

    # 5. Target the parent scoreboard container that includes teams, CRR, AND the match status line
    scoreboard = page.locator('div:has-text("RSA"):has-text("CRR:")').last.locator("..")
    scoreboard.wait_for(state="visible", timeout=20000)

    # 6. Extract visible text from the scoreboard banner and remove blank lines
    lines = [line.strip() for line in scoreboard.inner_text().splitlines() if line.strip()]
    joined = " ".join(lines)

    # 7. Extract 2-to-4 letter uppercase team abbreviations (excluding "CRR") and index [0] and [1]
    teams = [t for t in re.findall(r"\b[A-Z]{2,4}\b", joined) if t != "CRR"]
    team1 = teams[0] if len(teams) > 0 else "RSA"
    team2 = teams[1] if len(teams) > 1 else "BAN"

    # 8. Extract runs, wickets (optional), and overs using regular expressions
    score_match = re.search(r"(\d+)\s*(/\d+)?\s*\(([\d.]+)\)", joined)
    if score_match:
        runs = score_match.group(1)
        wickets = score_match.group(2) or ""
        overs = score_match.group(3)
        score_str = f"{team2} {runs}{wickets} ({overs} Ov)"
    else:
        score_str = f"{team2}"

    # 9. Find the line describing the live match status (e.g., "trail by", "need", "won")
    status = next(
        (l for l in lines if any(w in l.lower() for w in ["trail", "need", "lead", "won", "day", "opt"])),
        lines[-1]
    )

    # 10. Print the formatted live score and match status to the terminal
    print(score_str)
    print(f"{team1} vs {team2} - {status}")
    print()

    # 11. Capture a cropped screenshot of the complete scoreboard banner and save it
    scoreboard.screenshot(path="score.png")
    print("saved score.png")

    # 12. Close the browser and clean up resources
    browser.close()
