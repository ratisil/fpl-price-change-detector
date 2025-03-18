import requests, json, datetime
from pathlib import Path

# Constants and configuration
API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
DATA_DIR = Path("fpl_snapshots")
DATA_DIR.mkdir(exist_ok=True)

def fetch_snapshot():
    """Fetches the full snapshot of data from FPL API and returns players and teams."""
    response = requests.get(API_URL)
    data = response.json()
    players = data.get("elements", [])
    teams = data.get("teams", [])
    return players, {team["id"]: team["short_name"] for team in teams}

def save_snapshot(players, date):
    """Saves snapshot to a file named by date."""
    fname = DATA_DIR / f"{date:%Y-%m-%d}.json"
    with open(fname, "w") as f:
        json.dump(players, f)

def load_snapshot(date):
    """Loads snapshot from a given date."""
    fname = DATA_DIR / f"{date:%Y-%m-%d}.json"
    if fname.exists():
        with open(fname, "r") as f:
            return json.load(f)
    return []

def compare_snapshots(old, new):
    """Compares two snapshots and returns lists of risers and fallers.
       It returns a tuple: (risers, fallers) where each is a list of (player, cost difference)."""
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
    return risers, fallers

def format_price(cost):
    """Converts cost from integer (tenths) to formatted string in millions."""
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
    
    output_lines.append("")  # blank line
    
    # Price Fallers
    output_lines.append(f"Price Fallers! 📉 ({len(fallers)})")
    for player, diff in fallers:
        team = team_mapping.get(player.get("team"), "UNK")
        line = f"🔴 {player['web_name']} #{team} {format_price(player['now_cost'])}"
        output_lines.append(line)
    
    return "\n".join(output_lines)

def main():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    # Process 1: Fetch today's snapshot (players + team mapping)
    today_players, team_mapping = fetch_snapshot()
    save_snapshot(today_players, today)

    yesterday_players = load_snapshot(yesterday)
    if not yesterday_players:
        output = "No snapshot available for yesterday; cannot compare."
        print(output)
        with open("/app/logs/fpl_price_changes.log", "a") as log_file:
            log_file.write(output + "\n")
        return
    
    risers, fallers = compare_snapshots(yesterday_players, today_players)
    
    # Process 3: Format and output the results
    output = format_output(risers, fallers, team_mapping)
    print(output)
    with open("/app/logs/fpl_price_changes.log", "a") as log_file:
        log_file.write(output + "\n")

if __name__ == "__main__":
    main()