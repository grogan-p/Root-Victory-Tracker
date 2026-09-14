import os
import json
import tempfile
from flask import Flask, render_template, request, Response as FlaskResponse, redirect, url_for
from werkzeug.wrappers import Response
from waitress import serve
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WINS_FILE = os.path.join(BASE_DIR, "wins.json")
 
class Faction(Enum):
    MARQUISE   = "Marquise de Cat"
    EYRIE      = "Eyrie Dynasty"
    WOODLAND   = "Woodland Alliance"
    VAGABOND   = "Vagabond"
    LIZARDS    = "Lizard Cult"
    RIVERFOLK  = "Riverfolk Company"
    DUCHY      = "Underground Duchy"
    CORVIDS    = "Corvid Conspiracy"
    RATS       = "Lord of the Hundreds"
    BADGERS    = "Keepers in Iron"
    FROGS      = "Lilypad Diaspora"
    BATS       = "Twilight Council"
    SKUNKS     = "Knaves of the Deepwood"


DEFAULT_WINS = {
    "Group 1": {
        "Colin" : [Faction.EYRIE, Faction.LIZARDS, Faction.EYRIE, Faction.DUCHY, Faction.LIZARDS, Faction.LIZARDS, Faction.DUCHY, Faction.BATS, Faction.WOODLAND],
        "Patrick" : [Faction.WOODLAND, Faction.EYRIE, Faction.FROGS, Faction.RATS],
        "Dan" : [Faction.CORVIDS, Faction.RIVERFOLK, Faction.VAGABOND, Faction.BADGERS, Faction.FROGS],
        "Matthew" : [Faction.LIZARDS, Faction.RIVERFOLK],
        "Harry" : [Faction.DUCHY],
        "Sam" : [Faction.CORVIDS],
        "Max" : [Faction.DUCHY],
        "Nick" : [Faction.EYRIE],
        "Morrison" : [Faction.EYRIE]
    }
}


def save_wins(wins: dict[str, dict[str, list[Faction]]]) -> None:
    """Write the scoreboard to disk, storing factions by name."""

    payload = {
        group: {player: [faction.name for faction in victories] for player, victories in players.items()}
        for group, players in wins.items()
    }

    with tempfile.NamedTemporaryFile("w", dir=BASE_DIR, delete=False, encoding="utf-8") as file:
        json.dump(payload, file, indent=4)
        tmp_path = file.name

    os.replace(tmp_path, WINS_FILE)


def load_wins() -> dict[str, dict[str, list[Faction]]]:
    """Read the scoreboard from disk, seeding the file from DEFAULT_WINS on first run."""

    if not os.path.exists(WINS_FILE):
        save_wins(DEFAULT_WINS)

    with open(WINS_FILE, encoding="utf-8") as file:
        raw = json.load(file)

    return {
        group: {player: [Faction[name] for name in victories] for player, victories in players.items()}
        for group, players in raw.items()
    }


wins = load_wins()


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index() -> str | Response:
    """Main function"""

    group = request.args.get("group")
    if group not in wins:
        group = next(iter(wins))

    wins[group] = dict(sorted(wins[group].items(), key=lambda kv: len(kv[1]), reverse=True))
    # Sorting the players by most wins

    if request.method == "GET":
        return render_template('index.html', wins=wins[group], group=group, group_names=wins.keys(), factions=Faction)

    if request.method == "POST":
        if request.form["pwd"] == os.getenv("ADMIN_PWD"):
            wins[group][request.form["update-winner"]].append(
                Faction[request.form["update-winner-faction"]]
            )
            save_wins(wins)
            return redirect(url_for("index", group=group))
        return render_template('index.html', wins=wins[group], group=group, group_names=wins.keys(), factions=Faction)

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=2000)


#taskkill /f /im python.exe