"""Route requests with Flask"""

import requests
from flask import current_app as app
from flask import redirect, render_template

from tbj_statsapp import info

# Insert team name before feeds for team feeds
# e.g. https://www.mlb.com/bluejays/feeds/news/rss.xml
NEWS_RSS = "https://www.mlb.com/feeds/news/rss.xml"
STATSAPI_URL = "https://statsapi.mlb.com/"

request_session = requests.session()


@app.route("/")
def index():
    """Redirect to teams page"""
    return redirect("/teams")


@app.route("/teams")
def standing():
    """Render teams / standings page"""
    # Get standing info
    al_standings = info.get_standings(STATSAPI_URL, 103, request_session)
    nl_standings = info.get_standings(STATSAPI_URL, 104, request_session)

    # Sanity check to make sure both leagues have same number of divisions
    al_divisions, nl_divisions = [], []
    table_headers = ["W", "L", "Pct", "GB", "L10", "DIFF"]
    if len(al_standings) == len(nl_standings):
        for idx in range(len(al_standings)):
            al_divisions.append(
                info.get_division(
                    STATSAPI_URL, al_standings, idx, request_session
                )
            )
            nl_divisions.append(
                info.get_division(
                    STATSAPI_URL, nl_standings, idx, request_session
                )
            )
        # TODO: Raise error / alternative computation

        # Get league news
        recent_news = info.get_recent_news(NEWS_RSS, request_session)

    return render_template(
        "standings.html",
        table_headers=table_headers,
        leagues=[al_divisions, nl_divisions],
        recent_news=recent_news,
    )


@app.route("/<team_name>-<team_id>")
def team_page(team_name, team_id):
    """Render team specific page"""
    # Get team info

    # Get team specific news
    recent_news = info.get_recent_news(NEWS_RSS, request_session, team_name)

    return render_template(
        "team.html",
        recent_news=recent_news,
    )


@app.errorhandler(404)
def page_not_found(e):
    """Render 404 page"""
    return render_template("404.html"), 404
