"""Route requests with Flask"""

import requests
from flask import current_app as app
from flask import redirect, render_template

from tbj_statsapp import news, standings

# Insert team name before feeds for team feeds
# e.g. https://www.mlb.com/bluejays/feeds/news/rss.xml
NEWS_RSS = "https://www.mlb.com/feeds/news/rss.xml"
STATSAPI_URL = "https://statsapi.mlb.com/"


@app.route("/")
def index():
    """Redirect to teams page"""
    return redirect("/teams")


@app.route("/teams")
def teams():
    """Render teams page"""
    request_session = requests.session()

    # Get standing info
    al_standings = standings.get_standings(STATSAPI_URL, 103, request_session)
    nl_standings = standings.get_standings(STATSAPI_URL, 104, request_session)

    # Sanity check to make sure both leagues have same number of divisions
    al_divisions, nl_divisions = [], []
    table_headers = ["W", "L", "Pct", "GB", "L10", "DIFF"]
    if len(al_standings) == len(nl_standings):
        for idx in range(len(al_standings)):
            al_divisions.append(
                standings.get_division(
                    STATSAPI_URL, al_standings, idx, request_session
                )
            )
            nl_divisions.append(
                standings.get_division(
                    STATSAPI_URL, nl_standings, idx, request_session
                )
            )
        # TODO: Raise error / alternative computation

        # Get league news
        league_news = news.get_recent_news(NEWS_RSS, request_session)

    return render_template(
        "teams.html",
        table_headers=table_headers,
        al_divisions=al_divisions,
        nl_divisions=nl_divisions,
        league_news=league_news,
    )


@app.errorhandler(404)
def page_not_found(e):
    """Render 404 page"""
    return render_template("404.html"), 404
