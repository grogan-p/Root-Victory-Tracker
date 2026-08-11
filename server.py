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

# Anchored to this file so the save location doesn't depend on the working
# directory the server was launched from.
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
               "Colin" : [Faction.EYRIE, Faction.LIZARDS, Faction.EYRIE, Faction.DUCHY, Faction.LIZARDS, Faction.LIZARDS, Faction.DUCHY, Faction.BATS, Faction.WOODLAND],
               "Patrick" : [Faction.WOODLAND, Faction.EYRIE, Faction.FROGS, Faction.RATS],
               "Dan" : [Faction.CORVIDS, Faction.RIVERFOLK, Faction.VAGABOND, Faction.BADGERS],
               "Matthew" : [Faction.LIZARDS, Faction.RIVERFOLK],
               "Harry" : [Faction.DUCHY],
               "Sam" : [Faction.CORVIDS],
               "Max" : [Faction.DUCHY],
               "Nick" : []
               }


def save_wins(wins: dict[str, list[Faction]]) -> None:
    """Write the scoreboard to disk, storing factions by name."""

    payload = {player: [faction.name for faction in victories] for player, victories in wins.items()}

    with tempfile.NamedTemporaryFile("w", dir=BASE_DIR, delete=False, encoding="utf-8") as file:
        json.dump(payload, file, indent=4)
        tmp_path = file.name

    os.replace(tmp_path, WINS_FILE)


def load_wins() -> dict[str, list[Faction]]:
    """Read the scoreboard from disk, seeding the file from DEFAULT_WINS on first run."""

    if not os.path.exists(WINS_FILE):
        save_wins(DEFAULT_WINS)
        return {player: list(victories) for player, victories in DEFAULT_WINS.items()}

    with open(WINS_FILE, encoding="utf-8") as file:
        raw = json.load(file)

    return {player: [Faction[name] for name in names] for player, names in raw.items()}


wins = load_wins()


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index() -> str | Response:
    """Main function"""

    
    if request.method == "GET":
        return render_template('index.html', wins=wins, factions=Faction)

    if request.method == "POST":
        if request.form["pwd"] == os.getenv("ADMIN_PWD"):
            wins[request.form["update-winner"]].append(
                Faction[request.form["update-winner-faction"]]
            )
            save_wins(wins)
            return redirect(url_for("index"))
        return render_template('index.html', wins=wins, factions=Faction)

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=2000)