def get_standings(STATSAPI_URL, league, request_session):
    """Function to grab and return league specific standings by division"""
    standings = request_session.get(
        f"{STATSAPI_URL}/api/v1/standings?leagueId={league}"
    ).json()

    return standings["records"]


def get_division(STATSAPI_URL, standing, division_idx, request_session):
    """Function to grab and return necessary data for a specific division"""
    division_standings = {
        "name": None,
        "team_ids": [],
        "abbreviations": [],
        "logos": [],
        "wins": [],
        "losses": [],
        "pct": [],
        "gb": [],
        "l10": [],
        "diff": [],
    }

    for i, team_record in enumerate(standing[division_idx]["teamRecords"]):
        # Grab division info if first team processed
        if i == 0:
            division_name = request_session.get(
                f"{STATSAPI_URL}/{standing[division_idx]['division'].get('link')}"
            ).json()["divisions"][0]["nameShort"]
            division_standings["name"] = division_name

        # Team-related information
        division_standings["team_ids"].append(team_record["team"].get("id"))
        team_info = request_session.get(
            f"{STATSAPI_URL}/api/v1/teams/{division_standings['team_ids'][-1]}"
        ).json()
        division_standings["abbreviations"].extend(
            [team_info["teams"][0].get("abbreviation")]
        )
        division_standings["logos"].extend(
            [
                f"https://www.mlbstatic.com/team-logos/{division_standings['team_ids'][-1]}.svg"
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
                    [f"{split_record['wins']}-{split_record['losses']}"]
                )

    return division_standings
