import requests, json, datetime, logging, os, sys
from pathlib import Path

# Set up logging to both file and stdout.
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

file_handler = logging.FileHandler("/app/logs/fpl_price_changes.log", mode="w")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Constants and configuration - use absolute paths.
API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
DATA_DIR = Path("/app/fpl_snapshots")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_snapshot():
    logger.info("Fetching snapshot from FPL API.")
    response = requests.get(API_URL)
    data = response.json()
    players = data.get("elements", [])
    teams = data.get("teams", [])
    logger.info("Snapshot fetched successfully.")
    return players, {team["id"]: team["short_name"] for team in teams}

def save_snapshot(players, date):
    fname = DATA_DIR / f"{date:%Y-%m-%d}.json"
    logger.info(f"Saving snapshot to {fname}.")
    with open(fname, "w") as f:
        json.dump(players, f)
    logger.info("Snapshot saved.")
    mod_time = os.path.getmtime(fname)
    logger.info(f"Snapshot file last modified at {datetime.datetime.fromtimestamp(mod_time)}")

def load_snapshot(date):
    fname = DATA_DIR / f"{date:%Y-%m-%d}.json"
    logger.info(f"Loading snapshot from {fname}.")
    if fname.exists():
        with open(fname, "r") as f:
            data = json.load(f)
        logger.info("Snapshot loaded successfully.")
        return data
    logger.warning("Snapshot file does not exist.")
    return []

def compare_snapshots(old, new):
    logger.info("Comparing snapshots.")
    old_prices = {p["id"]: p["now_cost"] for p in old}
    risers, fallers = [], []
    for player in new:
        pid = player["id"]
        new_cost = player["now_cost"]
        old_cost = old_prices.get(pid)
        if old_cost is None:
            continue  # Skip if player wasn't present yesterday.
        if new_cost > old_cost:
            risers.append((player, new_cost - old_cost))
        elif new_cost < old_cost:
            fallers.append((player, new_cost - old_cost))
    logger.info(f"Comparison complete: {len(risers)} risers, {len(fallers)} fallers found.")
    return risers, fallers

def format_output(risers, fallers, team_mapping):
    today_str = datetime.date.today().strftime("%d/%m/%Y")
    
    # Case 4: No changes.
    if not risers and not fallers:
        return f"{today_str}\nNo price change today."
    
    output_lines = [today_str, ""]
    
    # Case 1: Risers (if any)
    if risers:
        output_lines.append(f"🟢 Price up +£0.1 📈 ({len(risers)})")
        for player, diff in risers:
            team = team_mapping.get(player.get("team"), "UNK")
            cost = player["now_cost"] / 10  # Convert tenths to pounds
            output_lines.append(f"• {player['web_name']} ({team}) £{cost:.1f}")
        output_lines.append("")
    
    # Case 2: Fallers (if any)
    if fallers:
        output_lines.append(f"🔴 Price down -£0.1 📉 ({len(fallers)})")
        for player, diff in fallers:
            team = team_mapping.get(player.get("team"), "UNK")
            cost = player["now_cost"] / 10
            output_lines.append(f"• {player['web_name']} ({team}) £{cost:.1f}")
    
    return "\n".join(output_lines)

def main():
    logger.info("Starting price change detection process.")
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    # Process 1: Fetch today's snapshot and team mapping.
    today_players, team_mapping = fetch_snapshot()
    save_snapshot(today_players, today)
    
    # Process 2: Load yesterday's snapshot and compare.
    yesterday_players = load_snapshot(yesterday)
    if not yesterday_players:
        message = "No snapshot available for yesterday; cannot compare."
        logger.warning(message)
        print(message)
        return
    
    risers, fallers = compare_snapshots(yesterday_players, today_players)
    
    # Process 3: Format the output.
    output = format_output(risers, fallers, team_mapping)
    logger.info("Formatted output ready.")
    logger.info("Process completed successfully. Output:\n" + output)
    print(output)
    
    # Convert output: replace newlines with <br> and encode the pound sign.
    html_output = output.replace("\n", "<br>").replace("£", "&pound;")
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FPL Price Changes</title>
</head>
<body>
    {html_output}
</body>
</html>"""
    html_filename = "/app/logs/fpl_prices.html"
    with open(html_filename, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)
    logger.info(f"HTML output written to {html_filename}.")

if __name__ == "__main__":
    main()
