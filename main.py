from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
import requests
from teamlogo import team_logo_dict

#Information of data resource
PLAYER_STATS_SEASON = 2022
PLAYER_ID_GET_URL = "https://www.balldontlie.io/api/v1/players"
PLAYER_STATS_URL = "https://www.balldontlie.io/api/v1/season_averages"
PLAYER_IMAGE_URL = f"http://data.nba.net/data/10s/prod/v1/{PLAYER_STATS_SEASON}/players.json"
UNKNOWN_IMAGE_URL = "https://i.ibb.co/yh2KG8P/unknown.jpg"
TEAM_URL = "https://www.balldontlie.io/api/v1/teams"

#Basic setup
app = Flask(__name__)
app.secret_key = 'Secret'
Bootstrap(app)

#Form for player
class PlayerForm(FlaskForm):
    first_name = StringField(label="Player's first name: ", validators=[DataRequired()])
    last_name = StringField(label="Player's last name: ", validators=[DataRequired()])

#Form for team
class TeamForm(FlaskForm):
    team = StringField(label="Team", validators=[DataRequired()])

#Main wbsite(player info)
@app.route("/", methods=["GET", "POST"])
def homepage():
    player_form = PlayerForm()
    if player_form.validate_on_submit() == True:
        first_name = player_form.first_name.data
        last_name = player_form.last_name.data
        full_name = first_name +" "+last_name

        # Call the player information API to get the ID and position
        PLAYER_PARAMS = {
            "search":full_name
        }
        PLAYER_INFO_RESPONSE = requests.get(url=PLAYER_ID_GET_URL, params=PLAYER_PARAMS)
        PLAYER_INFO_DATA = PLAYER_INFO_RESPONSE.json()
        #If found this player
        if len(PLAYER_INFO_DATA["data"]) > 0:
            PLAYER_ID = PLAYER_INFO_DATA["data"][0]["id"]
            PLAYER_FIRST_NAME = PLAYER_INFO_DATA["data"][0]["first_name"]
            PLAYER_LAST_NAME = PLAYER_INFO_DATA["data"][0]["last_name"]
            PLAYER_FULL_NAME = PLAYER_FIRST_NAME + " " + PLAYER_LAST_NAME
            PLAYER_TEAM = PLAYER_INFO_DATA["data"][0]["team"]["full_name"]
            PLAYER_POSITION = str(PLAYER_INFO_DATA["data"][0]["position"])
            PLAYER_FEET = str(PLAYER_INFO_DATA["data"][0]["height_feet"])
            PLAYER_INCHES = str(PLAYER_INFO_DATA["data"][0]["height_inches"])
            PLAYER_HEIGHT = PLAYER_FEET + "-" + PLAYER_INCHES
            #Handle the situation that we don't get this player's height
            if "None" in PLAYER_HEIGHT:
                PLAYER_HEIGHT = "N/A"

            #Get player's season stats, use the ID we got from above
            STATS_PARAMS = {
                "player_ids[]":PLAYER_ID,
                "season": PLAYER_STATS_SEASON
            }
            STATS_RESPONSE = requests.get(url=PLAYER_STATS_URL, params=STATS_PARAMS)
            STATS_DATA = STATS_RESPONSE.json()
            PLAYER_PPG = STATS_DATA["data"][0]["pts"]
            PLAYER_RPG = STATS_DATA["data"][0]["reb"]
            PLAYER_APG = STATS_DATA["data"][0]["ast"]

            #Get player's profile image - skip this part since the API for player's image is deprecated.
            # IMAGE_RESPONSE = requests.get(url=PLAYER_IMAGE_URL)
            # IMAGE_DATA = IMAGE_RESPONSE.json()
            # IMAGE_RAW_LIST = IMAGE_DATA["league"]["standard"]
            # IMAGE_INFO_LIST = []
            # IMAGE_ID_MAPPING_DICT = {}
            # for INFO in IMAGE_RAW_LIST:
            #     IMAGE_FULL_NAME = INFO["firstName"] + " " + INFO["lastName"]
            #     IMAGE_PLAYER_ID = INFO["personId"]
            #     IMAGE_ID_MAPPING_DICT[IMAGE_FULL_NAME] = IMAGE_PLAYER_ID
            #     IMAGE_INFO_LIST.append(IMAGE_FULL_NAME)
            #Photo url has the same structure, just the ID has slight difference
            # if PLAYER_FULL_NAME in IMAGE_INFO_LIST:
            #     IMAGE_ID = IMAGE_ID_MAPPING_DICT[PLAYER_FULL_NAME]
            #     PLAYER_PHOTO_URL = f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{IMAGE_ID}.png"
            #     return render_template("index.html", form=player_form, name=PLAYER_FULL_NAME, team=PLAYER_TEAM, position=PLAYER_POSITION, height=PLAYER_HEIGHT, ppg=PLAYER_PPG, rpg=PLAYER_RPG, apg=PLAYER_APG, image_url=PLAYER_PHOTO_URL, is_post=True, found=True)
            #Find the player but did not have image
            return render_template("index.html", form=player_form, name=PLAYER_FULL_NAME, team=PLAYER_TEAM, position=PLAYER_POSITION, height=PLAYER_HEIGHT, ppg=PLAYER_PPG, rpg=PLAYER_RPG, apg=PLAYER_APG, image_url=UNKNOWN_IMAGE_URL, is_post=True, found=True)

        #len(PLAYER_INFO_DATA["data"]) == 0:
        else:
            return render_template("index.html", form=player_form, not_found=True)

    return render_template("index.html", form=player_form)

#Team search website
@app.route("/team", methods=["GET", "POST"])
def team():
    team_form = TeamForm()
    if team_form.validate_on_submit() == True:
        team_input = team_form.team.data
        team_input = team_input.title()
        TEAM_RESPONSE = requests.get(url = TEAM_URL)
        TEAM_DATA_LIST = TEAM_RESPONSE.json()["data"]
        for team in TEAM_DATA_LIST:
            #User can either input heat or miami heat, both will work
            if team_input == team["full_name"] or team_input == team["name"]:
                team_name = team["full_name"]
                abbreviation = team["abbreviation"]
                conference = team["conference"]
                division = team["division"]
                image_name = team["name"].lower()
                #Use the team_logo_dict we have created in teamlogo
                logo_url = team_logo_dict[image_name]

                return render_template("team.html", form= team_form, team_name=team_name, abbreviation=abbreviation, conference=conference, division=division, logo_url=logo_url, is_post=True, found=True)

        return render_template("team.html", form=team_form, not_found = True)

    return render_template("team.html", form=team_form)

if __name__ == "__main__":
    app.run(debug=True)

