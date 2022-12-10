"""Route requests with Flask"""

from flask import current_app as app
from flask import redirect, render_template

from tbj_statsapp import info

# Insert team name before feeds for team feeds
# e.g. https://www.mlb.com/bluejays/feeds/news/rss.xml


@app.route("/")
def index():
    """Redirect to teams page"""
    return redirect("/teams")


@app.route("/teams")
def standing():
    """Render teams / standings page"""
    # Get standing info
    al_standings = info.get_standings(103)
    nl_standings = info.get_standings(104)

    # Sanity check to make sure both leagues have same number of divisions
    al_divisions, nl_divisions = [], []
    table_headers = ["W", "L", "Pct", "GB", "L10", "DIFF"]
    if len(al_standings) == len(nl_standings):
        for idx in range(len(al_standings)):
            al_divisions.append(info.get_division(al_standings, idx))
            nl_divisions.append(info.get_division(nl_standings, idx))
        # TODO: Raise error / alternative computation

        # Get league news
        recent_news = info.get_recent_news()

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
    team_info = info.get_team_info(int(team_id))

    # Get team roster
    team_roster = info.get_team_roster(
        int(team_id), str(team_info.get("season"))
    )
    team_roster["pitcher_header"] = [
        "Pos",
        "#",
        "Pitcher",
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
    recent_news = info.get_recent_news(team_name)

    return render_template(
        "team.html",
        team_info=team_info,
        team_roster=team_roster,
        recent_news=recent_news,
    )


@app.errorhandler(404)
def page_not_found(e):
    """Render 404 page"""
    return render_template("404.html"), 404
