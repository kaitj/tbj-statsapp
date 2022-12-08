from datetime import datetime

import xmltodict


def get_recent_news(rss, request_session, team=None):
    """Grab recent news for league / team"""

    # TODO: implement updating of news feed to grab team news
    # if team:

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
        news["title"] += [entry["title"]]
        news["link"] += [entry["link"]]
        news["author"] += [entry["dc:creator"]]
        news["image"] += [entry["image"]["@href"]]

        # Convert date to desired format
        date = datetime.strptime(
            entry["pubDate"],
            "%a, %d %b %Y %H:%M:%S %Z",
        )
        news["date"] += [date.strftime("%b %d %Y")]

    return news
