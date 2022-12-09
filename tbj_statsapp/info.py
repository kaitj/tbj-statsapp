from datetime import datetime

import xmltodict


def get_recent_news(rss, request_session, team=None):
    """Grab recent news for league / team"""

    # TODO: implement updating of news feed to grab team news
    if team:
        rss = rss.replace("feeds", f"{team}/feeds")

        # NEWS_RSS = "https://www.mlb.com/feeds/news/rss.xml"

    feed = request_session.get(rss, allow_redirects=False)
    entries = xmltodict.parse(feed.content)["rss"]["channel"]["item"]

    # Dict to store relevant news information
    news = {
        "title": [],
        "link": [],
        "author": [],
        "image": [],
        "date": [],
    }

    # Grab most recent 4 news stories
    for entry in entries[:4]:
        news["title"].extend([entry["title"]])
        news["link"].extend([entry["link"]])
        news["author"].extend([entry["dc:creator"]])
        news["image"].extend([entry["image"]["@href"]])

        # Convert date to desired format
        date = datetime.strptime(
            entry["pubDate"],
            "%a, %d %b %Y %H:%M:%S %Z",
        )
        news["date"] += [date.strftime("%b %d %Y")]

    return news


def get_standings(STATSAPI_URL, league, request_session):
    """Grab and return league specific standings by division"""
    standings = request_session.get(
        f"{STATSAPI_URL}/api/v1/standings?leagueId={league}"
    ).json()

    return standings["records"]


def get_division(STATSAPI_URL, standing, division_idx, request_session):
    """Grab and return necessary data for a specific division"""
    division_standings = {
        "name": None,
        "team_ids": [],
        "team_names": [],
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
        team_name = "".join(
            name.strip().lower()
            for name in team_info["teams"][0].get("teamName")
        )
        division_standings["team_names"].extend([team_name])
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
