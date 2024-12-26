from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from teamlogo import team_logo_dict
from balldontlie import BalldontlieAPI
import os

#Information of data resource
API_KEY = os.environ.get("api_key")
api = BalldontlieAPI(api_key=API_KEY)
UNKNOWN_IMAGE_URL = "https://i.ibb.co/yh2KG8P/unknown.jpg"

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

    #Post
    if player_form.validate_on_submit() == True:
        first_name = player_form.first_name.data.strip()
        last_name = player_form.last_name.data.strip()

        #Call the API to get response
        try:
            players_response = api.nba.players.list(first_name=first_name, last_name=last_name)
            PLAYER_INFO_DATA = players_response.data
            #If found this player
            if PLAYER_INFO_DATA:
                PLAYER_FIRST_NAME = PLAYER_INFO_DATA[0].first_name
                PLAYER_LAST_NAME = PLAYER_INFO_DATA[0].last_name
                PLAYER_FULL_NAME = PLAYER_FIRST_NAME + " " + PLAYER_LAST_NAME
                PLAYER_TEAM = PLAYER_INFO_DATA[0].team.full_name
                PLAYER_POSITION = PLAYER_INFO_DATA[0].position
                PLAYER_JERSEY_NUMBER = PLAYER_INFO_DATA[0].jersey_number
                PLAYER_COUNTRY = PLAYER_INFO_DATA[0].country if "None" not in PLAYER_INFO_DATA[0].country else "N/A"
                PLAYER_HEIGHT = str(PLAYER_INFO_DATA[0].height) if "None" not in str(PLAYER_INFO_DATA[0].height) else "N/A"
                PLAYER_WEIGHT = str(PLAYER_INFO_DATA[0].weight) if "None" not in str(PLAYER_INFO_DATA[0].weight) else "N/A"

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
                return render_template("index.html", form=player_form, name=PLAYER_FULL_NAME, team=PLAYER_TEAM, position=PLAYER_POSITION, height=PLAYER_HEIGHT, weight=PLAYER_WEIGHT, number=PLAYER_JERSEY_NUMBER, player_country=PLAYER_COUNTRY, image_url=UNKNOWN_IMAGE_URL, is_post=True, found=True)
            else:
                return render_template("index.html", form=player_form, not_found=True)
        #Something went wrong when parsing or handling the response of API
        except:
            return render_template("exception.html")

    #Get
    return render_template("index.html", form=player_form)

#Team search website
@app.route("/team", methods=["GET", "POST"])
def team():
    team_form = TeamForm()

    #Post
    if team_form.validate_on_submit() == True:
        team_input = team_form.team.data
        team_input = team_input.title()
        try:
            teams_response = api.nba.teams.list()
            TEAMS_INFO_DATA = teams_response.data
            for team in TEAMS_INFO_DATA:
                #User can either input heat or miami heat, both will work
                if team_input == team.full_name or team_input == team.name:
                    team_name = team.full_name
                    abbreviation = team.abbreviation
                    conference = team.conference
                    division = team.division
                    image_name = team.name.lower()
                    #Use the team_logo_dict we have created in teamlogo
                    logo_url = team_logo_dict[image_name]

                    return render_template("team.html", form= team_form, team_name=team_name, abbreviation=abbreviation, conference=conference, division=division, logo_url=logo_url, is_post=True, found=True)
            #No team has matched user's input
            return render_template("team.html", form=team_form, not_found = True)
        #Something went wrong when parsing or handling the response of API
        except:
            return render_template("except.html")

    #Get
    return render_template("team.html", form=team_form)

if __name__ == "__main__":
    app.run(debug=True)
