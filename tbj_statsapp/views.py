"""Route requests with Flask"""
import requests
from flask import current_app as app
from flask import redirect, render_template

from tbj_statsapp import api, info

request_session = requests.session()


@app.route("/")
def index():
    """Redirect to teams page"""
    return redirect("/teams")


@app.route("/teams")
def standing():
    """Render teams / standings page"""
    # Get standing info
    al_standings = api.get_standings(league_id=103, session=request_session)
    nl_standings = api.get_standings(league_id=104, session=request_session)

    # Sanity check to make sure both leagues have same number of divisions
    al_divisions, nl_divisions = [], []
    table_headers = ["W", "L", "Pct", "GB", "L10", "DIFF"]
    if len(al_standings) == len(nl_standings):
        for idx in range(len(al_standings)):
            al_divisions.append(
                info.get_divisions(
                    standing=al_standings,
                    division_idx=idx,
                    session=request_session,
                )
            )
            nl_divisions.append(
                info.get_divisions(
                    standing=nl_standings,
                    division_idx=idx,
                    session=request_session,
                )
            )
        # TODO: Raise error / alternative computation

    # Get league news
    recent_news = info.get_recent_news(session=request_session)

    return render_template(
        "standings.html",
        table_headers=table_headers,
        leagues=[al_divisions, nl_divisions],
        recent_news=recent_news,
    )


@app.route("/leaderboards")
def leaderboards():
    """Render leaderboards page

    TODO: Add team stats
    """

    # Get hitting leaders
    hitter_categories = {
        "homeRuns": "HR",
        "onBasePlusSlugging": "OPS",
        "stolenBases": "SB",
    }
    hitter_leaders = [
        info.get_leaders(
            category=category,
            session=request_session,
            player_type="hitting",
        )
        for category in hitter_categories.keys()
    ]

    # Get pitching leaders
    pitcher_categories = {
        "earnedRunAverage": "ERA",
        "strikeouts": "SO",
        "saves": "Saves",
    }
    pitcher_leaders = [
        info.get_leaders(
            category=category,
            player_type="pitching",
            session=request_session,
        )
        for category in pitcher_categories.keys()
    ]

    # Get league news
    recent_news = info.get_recent_news(
        session=request_session,
    )

    return render_template(
        "leaderboards.html",
        recent_news=recent_news,
        categories=[hitter_categories.values(), pitcher_categories.values()],
        leaders=[hitter_leaders, pitcher_leaders],
    )


@app.route("/<team_name>-<team_id>")
def team_page(team_name, team_id):
    """Render team specific page"""
    # Get team info
    team_info = info.get_team_info(
        team_id=int(team_id),
        session=request_session,
    )

    # Get team roster
    team_roster = info.get_team_roster(
        team_id=int(team_id),
        season=str(team_info.get("season")),
        session=request_session,
    )
    team_roster["pitcher_header"] = [
        "Age",
        "T",
        "IP",
        "ERA",
        "SO",
        "BB",
        "S0%",
        "BB%",
        "HR/9",
        "OPS",
    ]
    team_roster["hitter_header"] = [
        "Age",
        "B",
        "T",
        "PA",
        "H",
        "2B",
        "3B",
        "HR",
        "SB",
        "S0%",
        "BB%",
        "AVG",
        "OBP",
        "OPS",
    ]

    # Get team specific news
    recent_news = info.get_recent_news(session=request_session, team=team_name)

    return render_template(
        "team.html",
        team_info=team_info,
        team_roster=team_roster,
        recent_news=recent_news,
    )


@app.route("/<player_first_name>-<player_last_name>-<player_id>")
def player_page(player_first_name, player_last_name, player_id):
    """Render team specific page"""
    return redirect("404.html")


@app.errorhandler(404)
def page_not_found(e):
    """Render 404 page"""
    return render_template("404.html"), 404
