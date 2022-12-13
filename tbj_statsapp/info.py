from collections import defaultdict
from datetime import datetime

from tbj_statsapp import api, utils


def get_recent_news(session, team=None):
    """Grab recent league / team news"""
    news_entries = api.get_news(session=session, team=team)

    # Grab most recent 4 news stories
    news = defaultdict(list)
    for entry in news_entries[:4]:
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


def get_divisions(standing, division_idx, session):
    """Grab and return necessary data for a specific division"""
    division_standings = defaultdict(list)

    for i, team_record in enumerate(standing[division_idx]["teamRecords"]):
        # Grab division info if first team processed
        if i == 0:
            division_name = api.get_division(
                division_id=standing[division_idx]["division"].get("id"),
                session=session,
            )
            division_standings["name"] = division_name.get("nameShort")

        # Team-related information
        division_standings["team_ids"].append(team_record["team"].get("id"))
        team_api = api.get_team(
            team_id=team_record["team"].get("id"), session=session
        )
        division_standings["abbreviations"].extend(
            [team_api.get("abbreviation")]
        )
        team_name = "".join(
            name.strip().lower() for name in team_api.get("teamName")
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


def get_team_info(team_id, session):
    """Get team related info"""
    team_api = api.get_team(team_id, session=session)
    league_standings = api.get_standings(
        team_api["league"]["id"], session=session
    )

    for standings in league_standings:
        if standings["division"]["id"] == team_api["division"].get("id"):
            standings = standings["teamRecords"]
            break

    # Get team info
    team_info = defaultdict()
    team_info["team_id"] = team_id
    team_info["logo"] = f"https://www.mlbstatic.com/team-logos/{team_id}.svg"
    team_info["name"] = team_api.get("name")
    team_info["club_name"] = team_api.get("clubName").replace(" ", "").lower()
    team_info["abbreviation"] = team_api.get("abbreviation")
    team_info["division"] = api.get_division(
        division_id=team_api["division"].get("id"),
        session=session,
    ).get("nameShort")
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
    team_info["division_rank"] = utils.rank_map(
        int(team_standing["divisionRank"])
    )
    team_info["record"] = (
        f'{team_standing["leagueRecord"].get("wins")}-'
        + f'{team_standing["leagueRecord"].get("losses")} '
        + f'({team_standing["leagueRecord"].get("pct")})'
    )
    team_info["gb"] = team_standing.get("divisionGamesBack")

    return team_info


def get_team_roster(team_id, season, session):
    """Get team rosters, grouped by hitters and pitchers"""
    roster = api.get_rosters(team_id=team_id, session=session)

    # Default value for empty stats
    null = "-"

    team_rosters = defaultdict(lambda: defaultdict(list))
    for player in roster:
        player_api = api.get_player(
            player_id=player["person"].get("id"),
            session=session,
        )
        # Pitchers
        if player_api["primaryPosition"].get("code") == "1":
            pitching_stats, last_played_season = api.get_player_stats(
                player_id=player_api.get("id"),
                category="pitching",
                season=season,
                session=session,
            )

            # Player info
            team_rosters["pitchers"]["player_id"].append(player_api.get("id"))
            team_rosters["pitchers"]["position"].extend(
                [player_api["primaryPosition"].get("abbreviation", null)]
            )
            team_rosters["pitchers"]["jersey_number"].extend(
                [player_api.get("primaryNumber", null)]
            )
            team_rosters["pitchers"]["photo"].extend(
                [
                    "https://content.mlb.com/images/headshots/current/60x60/"
                    + f"{player_api.get('id')}.png"
                ]
            )
            team_rosters["pitchers"]["first_name"].extend(
                [player_api.get("firstName")]
            )
            team_rosters["pitchers"]["last_name"].extend(
                [player_api.get("lastName")]
            )
            team_rosters["pitchers"]["age"].extend(
                [player_api.get("currentAge")]
            )
            team_rosters["pitchers"]["throw_hand"].extend(
                [player_api["pitchHand"].get("code")]
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
            hitting_stats, last_played_season = api.get_player_stats(
                player_id=player_api.get("id"),
                category="hitting",
                season=season,
                session=session,
            )
            # Player info
            team_rosters["hitters"]["player_id"].append(player_api.get("id"))
            team_rosters["hitters"]["position"].extend(
                [player_api["primaryPosition"].get("abbreviation", null)]
            )
            team_rosters["hitters"]["jersey_number"].extend(
                [player_api.get("primaryNumber", null)]
            )
            team_rosters["hitters"]["photo"].extend(
                [
                    "https://content.mlb.com/images/headshots/current/60x60/"
                    + f"{player_api.get('id')}.png"
                ]
            )
            team_rosters["hitters"]["first_name"].extend(
                [player_api.get("firstName")]
            )
            team_rosters["hitters"]["last_name"].extend(
                [player_api.get("lastName")]
            )
            team_rosters["hitters"]["age"].extend(
                [player_api.get("currentAge")]
            )
            team_rosters["hitters"]["bat_side"].extend(
                [player_api["batSide"].get("code")]
            )
            team_rosters["hitters"]["throw_hand"].extend(
                [player_api["pitchHand"].get("code")]
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


def get_player(player_id, session):
    """Get play profile information"""
    player_api = api.get_player(player_id, session)

    player = defaultdict()
    player["id"] = player_api.get("id")
    player["name"] = player_api.get("fullName")
    player["photo"] = (
        "https://content.mlb.com/images/headshots/current/60x60/"
        + f"{player_api.get('id')}@2x.png"
    )
    player["position"] = player_api["primaryPosition"].get("abbreviation")
    #     team
    player["bat_side"] = player_api["batSide"].get("code")
    player["pitch_hand"] = player_api["pitchHand"].get("code")
    player["age"] = player_api.get("currentAge")
    player["height"] = (
        player_api.get("height").replace("\\'", "'").replace(" ", "")
    )
    player["weight"] = player_api.get("weight")
    player["draft_year"] = player_api.get("draftYear", "Undrafted")

    return player


def get_leaders(category, player_type, session):
    """Grab leaders for input category"""
    category_leaders = api.get_category(
        category=category,
        session=session,
    )

    # Grab correct player type
    for i in range(len(category_leaders)):
        if category_leaders[i].get("statGroup") == player_type:
            category_leaders = category_leaders[i]["leaders"]
            break

    leaders = defaultdict(list)
    for player in category_leaders:
        # Get stat info
        leaders["rank"].append(player.get("rank"))
        leaders["value"].extend([player.get("value")])

        # Get player info
        player_api = api.get_player(
            player_id=player["person"].get("id"),
            session=session,
        )
        leaders["position"].extend(
            [player_api["primaryPosition"].get("abbreviation")]
        )
        leaders["first_name"].extend([player_api.get("firstName")])
        leaders["last_name"].extend([player_api.get("lastName")])
        leaders["player_id"].append(player_api.get("id"))
        leaders["player_photo"].extend(
            [
                "https://content.mlb.com/images/headshots/current/60x60/"
                + f"{player_api.get('id')}.png"
            ]
        )

    return leaders
