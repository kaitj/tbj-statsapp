"""Route requests with Flask"""
import requests
from flask import current_app as app
from flask import redirect, render_template
from flask import session as flask_session

from tbj_statsapp import api, info

request_session = requests.session()
# Add retries (max 5 attempts) in case session is closed on remote end
adapter = requests.adapters.HTTPAdapter(max_retries=5)
request_session.mount("https://", adapter)
request_session.mount("http://", adapter)


@app.route("/")
def index():
    """Redirect to teams page"""
    return redirect("/teams")


@app.route("/teams")
def standing():
    """Render teams / standings page"""
    flask_session["al_divisions"] = flask_session.get("al_divisions", [])
    flask_session["nl_divisions"] = flask_session.get("nl_divisions", [])
    table_headers = ["W", "L", "Pct", "GB", "L10", "DIFF"]

    # Sanity check to make sure both leagues have same number of divisions
    if not flask_session["al_divisions"] or not flask_session["nl_divisions"]:
        # Get standing info
        al_standings = api.get_standings(
            league_id=103, session=request_session
        )
        nl_standings = api.get_standings(
            league_id=104, session=request_session
        )

        if len(al_standings) == len(nl_standings):
            for idx in range(len(al_standings)):
                # Get divisions
                flask_session["al_divisions"].append(
                    info.get_divisions(
                        standing=al_standings,
                        division_idx=idx,
                        session=request_session,
                    )
                )
                flask_session["nl_divisions"].append(
                    info.get_divisions(
                        standing=nl_standings,
                        division_idx=idx,
                        session=request_session,
                    )
                )
                # Get teamids
                for idx, name in enumerate(
                    flask_session["al_divisions"][-1]["team_names"]
                ):
                    flask_session[name] = flask_session["al_divisions"][-1][
                        "team_ids"
                    ][idx]
                for idx, name in enumerate(
                    flask_session["nl_divisions"][-1]["team_names"]
                ):
                    flask_session[name] = flask_session["nl_divisions"][-1][
                        "team_ids"
                    ][idx]

        # TODO: Raise error / alternative computation

    # Get league news
    recent_news = info.get_recent_news(session=request_session)

    return render_template(
        "standings.html",
        table_headers=table_headers,
        leagues=[
            flask_session.get("al_divisions"),
            flask_session.get("nl_divisions"),
        ],
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

    flask_session["hitter_leaders"] = flask_session.get(
        "hitter_leaders",
        [
            info.get_leaders(
                category=category,
                session=request_session,
                player_type="hitting",
            )
            for category in hitter_categories.keys()
        ],
    )

    # Get pitching leaders
    pitcher_categories = {
        "earnedRunAverage": "ERA",
        "strikeouts": "SO",
        "saves": "Saves",
    }
    flask_session["pitcher_leaders"] = flask_session.get(
        "pitcher_leaders",
        [
            info.get_leaders(
                category=category,
                player_type="pitching",
                session=request_session,
            )
            for category in pitcher_categories.keys()
        ],
    )

    # Get league news
    recent_news = info.get_recent_news(
        session=request_session,
    )

    return render_template(
        "leaderboards.html",
        recent_news=recent_news,
        categories=[hitter_categories.values(), pitcher_categories.values()],
        leaders=[
            flask_session.get("hitter_leaders"),
            flask_session.get("pitcher_leaders"),
        ],
    )


@app.route("/teams/<team_name>")
def team_page(team_name):
    """Render team specific page"""
    team_id = flask_session.get(team_name)

    # Get team info
    flask_session[f"{team_id}-info"] = flask_session.get(
        f"{team_id}-info",
        info.get_team_info(
            team_id=team_id,
            session=request_session,
        ),
    )

    # Get team roster
    flask_session[f"{team_id}-roster"] = flask_session.get(
        f"{team_id}-roster",
        info.get_team_roster(
            team_id=int(team_id),
            season=str(flask_session[f"{team_id}-info"].get("season")),
            session=request_session,
        ),
    )

    # Save player information in server-side session
    for player_id in flask_session[f"{team_id}-roster"]["pitchers"].get(
        "player_id"
    ):
        flask_session[str(player_id)] = team_id
    for player_id in flask_session[f"{team_id}-roster"]["hitters"].get(
        "player_id"
    ):
        flask_session[str(player_id)] = team_id

    pitcher_header = [
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
    hitter_header = [
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
        team_info=flask_session.get(f"{team_id}-info"),
        team_roster=flask_session.get(f"{team_id}-roster"),
        pitcher_header=pitcher_header,
        hitter_header=hitter_header,
        recent_news=recent_news,
    )


@app.route("/<player_first_name>-<player_last_name>-<player_id>")
def player_page(player_first_name, player_last_name, player_id):
    """Render team specific page"""
    # Get player info
    flask_session[f"{player_id}-info"] = flask_session.get(
        f"{player_id}-info",
        info.get_player(
            player_id=player_id,
            session=request_session,
        ),
    )
    position = flask_session.get(f"{player_id}-info").get("position")

    # Get team id, or search for player if not already cached
    team_id = flask_session.get(
        str(player_id),
        api.search_players(
            player_id=int(player_id),
            session=request_session,
        ),
    )

    # Get team info
    flask_session[f"{team_id}-info"] = flask_session.get(
        f"{team_id}-info",
        info.get_team_info(
            team_id=team_id,
            session=request_session,
        ),
    )

    # Get career stats
    flask_session[f"{player_id}-career"] = flask_session.get(
        f"{player_id}-stats",
        info.get_career_stats(
            player_id=player_id,
            category="pitching" if position == "P" else "hitting",
            session=request_session,
        ),
    )
    pitcher_headers = [
        "G",
        "IP",
        "W",
        "L",
        "SV",
        "ERA",
        "WHIP",
        "H",
        "R",
        "SO",
        "BB",
        "HR/9",
        "OPS",
    ]
    hitter_headers = [
        "G",
        "PA",
        "AB",
        "R",
        "H",
        "2B",
        "3B",
        "HR",
        "RBI",
        "SB",
        "BB",
        "SO",
        "OBP",
        "SLG",
        "OPS",
    ]

    return render_template(
        "player.html",
        player_info=flask_session.get(f"{player_id}-info"),
        player_career=flask_session.get(f"{player_id}-career").to_dict(
            orient="list"
        ),
        team_info=flask_session.get(f"{team_id}-info"),
        table_header=pitcher_headers if position == "P" else hitter_headers,
    )


@app.errorhandler(404)
def page_not_found(e):
    """Render 404 page"""
    return render_template("404.html"), 404
