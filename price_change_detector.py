import requests, json, datetime, logging
from pathlib import Path

# Configure logging: overwrite the log file each run (only today's logs)
logging.basicConfig(
    filename="/app/logs/fpl_price_changes.log",
    filemode="w",  # Use "w" to overwrite on each run; change to "a" to append if desired
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

# Constants and configuration
API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
DATA_DIR = Path("fpl_snapshots")
DATA_DIR.mkdir(exist_ok=True)

def fetch_snapshot():
    logging.info("Fetching snapshot from FPL API.")
    response = requests.get(API_URL)
    data = response.json()
    players = data.get("elements", [])
    teams = data.get("teams", [])
    logging.info("Snapshot fetched successfully.")
    return players, {team["id"]: team["short_name"] for team in teams}

def save_snapshot(players, date):
    fname = DATA_DIR / f"{date:%Y-%m-%d}.json"
    logging.info(f"Saving snapshot to {fname}.")
    with open(fname, "w") as f:
        json.dump(players, f)
    logging.info("Snapshot saved.")

def load_snapshot(date):
    fname = DATA_DIR / f"{date:%Y-%m-%d}.json"
    logging.info(f"Loading snapshot from {fname}.")
    if fname.exists():
        with open(fname, "r") as f:
            data = json.load(f)
        logging.info("Snapshot loaded successfully.")
        return data
    logging.warning("Snapshot file does not exist.")
    return []

def compare_snapshots(old, new):
    logging.info("Comparing snapshots.")
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
    logging.info(f"Comparison complete: {len(risers)} risers, {len(fallers)} fallers found.")
    return risers, fallers

def format_price(cost):
    return f"£{cost/10:.1f}m"

def format_output(risers, fallers, team_mapping):
    today_str = datetime.date.today().strftime("%d/%m/%Y")
    output_lines = [today_str, ""]
    
    # Price Risers
    output_lines.append(f"Price Risers! 📈 ({len(risers)})")
    for player, diff in risers:
        team = team_mapping.get(player.get("team"), "UNK")
        line = f"🟢 {player['web_name']} #{team} {format_price(player['now_cost'])}"
        output_lines.append(line)
    
    output_lines.append("")
    
    # Price Fallers
    output_lines.append(f"Price Fallers! 📉 ({len(fallers)})")
    for player, diff in fallers:
        team = team_mapping.get(player.get("team"), "UNK")
        line = f"🔴 {player['web_name']} #{team} {format_price(player['now_cost'])}"
        output_lines.append(line)
    
    return "\n".join(output_lines)

def main():
    logging.info("Starting price change detection process.")
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    # Process 1: Fetch today's snapshot and team mapping
    today_players, team_mapping = fetch_snapshot()
    save_snapshot(today_players, today)
    
    # Process 2: Load yesterday's snapshot and compare
    yesterday_players = load_snapshot(yesterday)
    if not yesterday_players:
        message = "No snapshot available for yesterday; cannot compare."
        logging.warning(message)
        print(message)
        return
    
    risers, fallers = compare_snapshots(yesterday_players, today_players)
    
    # Process 3: Format and output the results
    output = format_output(risers, fallers, team_mapping)
    logging.info("Formatted output ready.")
    print(output)
    logging.info("Process completed successfully. Output:\n" + output)

if __name__ == "__main__":
    main()
