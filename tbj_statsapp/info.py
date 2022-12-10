from collections import defaultdict
from datetime import datetime

import requests
import xmltodict

from tbj_statsapp.utils import rank_map

NEWS_RSS = "https://www.mlb.com/feeds/news/rss.xml"
STATSAPI_URL = "https://statsapi.mlb.com/"
REQUEST_SESSION = requests.session()


def get_recent_news(team=None, session=REQUEST_SESSION, rss=NEWS_RSS):
    """Grab recent news for league / team"""

    # TODO: implement updating of news feed to grab team news
    if team:
        rss = rss.replace("feeds", f"{team}/feeds")

        # NEWS_RSS = "https://www.mlb.com/feeds/news/rss.xml"

    feed = session.get(rss, allow_redirects=False)
    entries = xmltodict.parse(feed.content)["rss"]["channel"]["item"]

    # Dict to store relevant news information
    news = defaultdict(list)

    # Grab most recent 4 news stories
    for entry in entries[:4]:
        news["title"].extend([entry.get("title")])
        news["link"].extend([entry.get("link")])
        news["author"].extend([entry.get("dc:creator")])
        news["image"].extend([entry["image"].get("@href")])

        # Convert date to desired format
        date = datetime.strptime(
            entry.get("pubDate"),
            "%a, %d %b %Y %H:%M:%S %Z",
        )
        news["date"] += [date.strftime("%b %d %Y")]

    return news


def get_player_info(player_id, stats_api=STATSAPI_URL):
    """Get player information"""
    player_info = requests.get(f"{stats_api}/api/v1/people/{player_id}").json()

    return player_info.get("people")[0]


def get_player_stats(player_id, category, season=None, stats_api=STATSAPI_URL):
    """Get stats for a given player for a given category"""
    stats = (
        requests.get(
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


def get_standings(league, session=REQUEST_SESSION, stats_api=STATSAPI_URL):
    """Grab and return league specific standings by division"""
    standings = session.get(
        f"{stats_api}/api/v1/standings?leagueId={league}"
    ).json()

    return standings.get("records")


def get_division(
    standing, division_idx, session=REQUEST_SESSION, stats_api=STATSAPI_URL
):
    """Grab and return necessary data for a specific division"""
    division_standings = defaultdict(list)

    for i, team_record in enumerate(standing[division_idx]["teamRecords"]):
        # Grab division info if first team processed
        if i == 0:
            division_name = (
                session.get(
                    f"{stats_api}/"
                    + f"{standing[division_idx]['division'].get('link')}"
                )
                .json()["divisions"][0]
                .get("nameShort")
            )
            division_standings["name"] = division_name

        # Team-related information
        division_standings["team_ids"].append(team_record["team"].get("id"))
        team_info = session.get(
            f"{stats_api}/api/v1/teams/"
            + f"{division_standings.get('team_ids')[-1]}"
        ).json()
        division_standings["abbreviations"].extend(
            [team_info["teams"][0].get("abbreviation")]
        )
        team_name = "".join(
            name.strip().lower()
            for name in team_info["teams"][0].get("teamName")
        )
        division_standings["team_names"].extend([team_name])
        division_standings["logos"].extend(
            [
                "https://www.mlbstatic.com/team-logos/"
                + f"{division_standings['team_ids'][-1]}.svg"
            ]
        )

        # Team stats
        division_standings["wins"].append(team_record.get("wins"))
        division_standings["losses"].append(team_record.get("losses"))
        division_standings["pct"].append(team_record.get("winningPercentage"))
        division_standings["gb"].extend([team_record.get("wildCardGamesBack")])
        division_standings["diff"].append(
            team_record.get("runsScored") - team_record.get("runsAllowed")
        )

        for split_record in team_record["records"]["splitRecords"]:
            if split_record["type"] == "lastTen":
                division_standings["l10"].extend(
                    [
                        f"{split_record.get('wins')}-"
                        + f"{split_record.get('losses')}"
                    ]
                )

    return division_standings


def get_team_info(team_id, session=REQUEST_SESSION, stats_api=STATSAPI_URL):
    """Get team related info"""
    team_api = session.get(f"{stats_api}/api/v1/teams/{team_id}").json()[
        "teams"
    ][0]
    standings = get_standings(team_api["league"]["id"])[0]["teamRecords"]

    # Get team info
    team_info = defaultdict()
    team_info["team_id"] = team_id
    team_info["logo"] = f"https://www.mlbstatic.com/team-logos/{team_id}.svg"
    team_info["name"] = team_api.get("name")
    team_info["division"] = (
        session.get(
            f'{stats_api}/api/v1/divisions/{team_api["division"]["id"]}'
        )
        .json()["divisions"][0]
        .get("nameShort")
    )
    team_info["venue"] = team_api["venue"].get("name")
    team_info["venue_img"] = (
        "https://prod-gameday.mlbstatic.com/"
        + "responsive-gameday-assets/1.2.0/images/fields/"
        + f'{team_api["venue"]["id"]}.svg'
    )
    team_info["season"] = team_api.get("season")

    # Get team standing
    for team_standing in standings:
        if team_standing["team"].get("id") == team_id:
            break
    team_info["division_rank"] = rank_map(int(team_standing["divisionRank"]))
    team_info["record"] = (
        f'{team_standing["leagueRecord"].get("wins")}-'
        + f'{team_standing["leagueRecord"].get("losses")} '
        + f'({team_standing["leagueRecord"].get("pct")})'
    )
    team_info["gb"] = team_standing.get("divisionGamesBack")

    return team_info


def get_team_roster(
    team_id, season, session=REQUEST_SESSION, stats_api=STATSAPI_URL
):
    """Get team rosters, grouped by hitters and pitchers

    TODO: Replace player stats with function
    """
    team_api = session.get(
        f"{stats_api}/api/v1/teams/{team_id}/roster"
    ).json()["roster"]

    # Default value for empty stats
    null = "-"
    team_rosters = defaultdict(lambda: defaultdict(list))

    for player in team_api:
        player_info = get_player_info(player["person"].get("id"))
        # Pitchers
        if player_info["primaryPosition"].get("code") == "1":
            pitching_stats, last_played_season = get_player_stats(
                player_info.get("id"), "pitching", season
            )

            # Player info
            team_rosters["pitchers"]["player_id"].append(player_info.get("id"))
            team_rosters["pitchers"]["position"].extend(
                [player_info["primaryPosition"].get("abbreviation", null)]
            )
            team_rosters["pitchers"]["jersey_number"].extend(
                [player_info.get("primaryNumber", null)]
            )
            team_rosters["pitchers"]["photo"].extend(
                [
                    "https://content.mlb.com/images/headshots/current/60x60/"
                    + f"{player_info.get('id')}.png"
                ]
            )
            team_rosters["pitchers"]["first_name"].extend(
                [player_info.get("firstName")]
            )
            team_rosters["pitchers"]["last_name"].extend(
                [player_info.get("lastName")]
            )
            team_rosters["pitchers"]["age"].extend(
                [player_info.get("currentAge")]
            )
            team_rosters["pitchers"]["throw_hand"].extend(
                [player_info["pitchHand"].get("code")]
            )
            team_rosters["pitchers"]["last_played"].extend(
                [last_played_season]
            )

            # Player stats
            team_rosters["pitchers"]["ip"].extend(
                [pitching_stats.get("inningsPitched", null)]
            )
            team_rosters["pitchers"]["era"].extend(
                [pitching_stats.get("era", null)]
            )
            team_rosters["pitchers"]["hr_per_9"].extend(
                [pitching_stats.get("homeRunsPer9", null)]
            )
            team_rosters["pitchers"]["ops"].extend(
                [pitching_stats.get("ops", null)]
            )
            strikeouts = pitching_stats.get("strikeOuts", null)
            base_on_balls = pitching_stats.get("baseOnBalls", null)
            batters_faced = pitching_stats.get("battersFaced", null)
            team_rosters["pitchers"]["strikeouts"].extend([strikeouts])
            team_rosters["pitchers"]["base_on_balls"].extend([base_on_balls])
            team_rosters["pitchers"]["strikeout_pct"].extend(
                [
                    f"{round(strikeouts / batters_faced * 100)}%"
                    if not isinstance(batters_faced, str)
                    else null
                ]
            )
            team_rosters["pitchers"]["bb_pct"].extend(
                [
                    f"{round(base_on_balls / batters_faced * 100)}%"
                    if not isinstance(batters_faced, str)
                    else null
                ]
            )

        # Hitters
        else:
            hitting_stats, last_played_season = get_player_stats(
                player_info.get("id"), "hitting", season
            )
            # Player info
            team_rosters["hitters"]["player_id"].append(player_info.get("id"))
            team_rosters["hitters"]["position"].extend(
                [player_info["primaryPosition"].get("abbreviation", null)]
            )
            team_rosters["hitters"]["jersey_number"].extend(
                [player_info.get("primaryNumber", null)]
            )
            team_rosters["hitters"]["photo"].extend(
                [
                    "https://content.mlb.com/images/headshots/current/60x60/"
                    + f"{player_info.get('id')}.png"
                ]
            )
            team_rosters["hitters"]["first_name"].extend(
                [player_info.get("firstName")]
            )
            team_rosters["hitters"]["last_name"].extend(
                [player_info.get("lastName")]
            )
            team_rosters["hitters"]["age"].extend(
                [player_info.get("currentAge")]
            )
            team_rosters["hitters"]["bat_side"].extend(
                [player_info["batSide"].get("code")]
            )
            team_rosters["hitters"]["throw_hand"].extend(
                [player_info["pitchHand"].get("code")]
            )
            team_rosters["hitters"]["last_played"].extend([last_played_season])

            # Player stats
            team_rosters["hitters"]["plate_appearances"].extend(
                [hitting_stats.get("plateAppearances", null)]
            )
            team_rosters["hitters"]["hits"].extend(
                [hitting_stats.get("hits", null)]
            )
            team_rosters["hitters"]["doubles"].extend(
                [hitting_stats.get("doubles", null)]
            )
            team_rosters["hitters"]["triples"].extend(
                [hitting_stats.get("triples", null)]
            )
            team_rosters["hitters"]["hrs"].extend(
                [hitting_stats.get("homeRuns", null)]
            )
            team_rosters["hitters"]["stolen_bases"].extend(
                [hitting_stats.get("stolenBases", null)]
            )
            team_rosters["hitters"]["avg"].extend(
                [hitting_stats.get("avg", null)]
            )
            team_rosters["hitters"]["obp"].extend(
                [hitting_stats.get("obp", null)]
            )
            team_rosters["hitters"]["ops"].extend(
                [hitting_stats.get("ops", null)]
            )
            strikeouts = hitting_stats.get("strikeOuts", null)
            base_on_balls = hitting_stats.get("baseOnBalls", null)
            at_bats = hitting_stats.get("atBats", null)
            team_rosters["hitters"]["base_on_balls"].extend([base_on_balls])
            team_rosters["hitters"]["strikeout_pct"].extend(
                [
                    f"{round(strikeouts / at_bats * 100)}%"
                    if not isinstance(at_bats, str)
                    else null
                ]
            )
            team_rosters["hitters"]["bb_pct"].extend(
                [
                    f"{round(base_on_balls / at_bats * 100)}%"
                    if not isinstance(at_bats, str)
                    else null
                ]
            )

            return team_rosters
