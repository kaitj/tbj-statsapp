import xmltodict

NEWS_RSS = "https://www.mlb.com/feeds/news/rss.xml"
STATSAPI_URL = "https://statsapi.mlb.com/"


def get_news(session, team=None, rss=NEWS_RSS):
    """Grab news for league / team"""

    if team:
        rss = rss.replace("feeds", f"{team}/feeds")

    feed = session.get(rss, allow_redirects=False)
    entries = xmltodict.parse(feed.content)["rss"]["channel"]["item"]

    return entries


def get_player(player_id, session, stats_api=STATSAPI_URL):
    """Get player information from statsapi"""
    player_api = session.get(f"{stats_api}/api/v1/people/{player_id}").json()

    return player_api.get("people")[0]


def get_rosters(team_id, session, stats_api=STATSAPI_URL):
    roster = session.get(f"{stats_api}/api/v1/teams/{team_id}/roster").json()

    return roster.get("roster")


def get_player_stats(
    player_id, category, session, season=None, stats_api=STATSAPI_URL
):
    """Get stats for a given player for a given category from statsapi"""
    stats = (
        session.get(
            f"{stats_api}/api/v1/people/{player_id}?hydrate=stats"
            + f"(group=[{category}],type=[yearByYear])"
        )
        .json()["people"][0]
        .get("stats")
    )

    # If player has never played in MLB
    if not stats:
        return {}, None
    stats = stats[0].get("splits")

    if season:
        for i in range(len(stats)):
            # Get total season stats (if multiple teams)
            if stats[i]["season"] == season and "team" not in stats[i].keys():
                return stats[i].get("stat"), None
            # If didn't pitch previous season, get last season pitched
            else:
                return stats[-1].get("stat"), stats[-1].get("season")

    return stats


def get_standings(league_id, session, stats_api=STATSAPI_URL):
    """Grab and return league specific standings by division from statsapi"""
    standings = session.get(
        f"{stats_api}/api/v1/standings?leagueId={league_id}"
    ).json()

    return standings.get("records")


def get_division(division_id, session, stats_api=STATSAPI_URL):
    """Grab division info from statsapi"""
    division = session.get(
        f"{stats_api}/api/v1/divisions/{division_id}"
    ).json()

    return division["divisions"][0]


def get_team(team_id, session, stats_api=STATSAPI_URL):
    """Grab team info from statsapi"""
    team_api = session.get(f"{stats_api}/api/v1/teams/{team_id}").json()

    return team_api["teams"][0]


def get_category(category, session, stats_api=STATSAPI_URL):
    """Get leaders for input category from statsapi"""
    category_leaders = session.get(
        f"{stats_api}/api/v1/stats/leaders?leaderCategories={category}"
    ).json()

    return category_leaders["leagueLeaders"]
