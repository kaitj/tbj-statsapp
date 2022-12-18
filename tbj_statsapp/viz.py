from plotly import graph_objects as go

PRIMARY_COLOUR = "#244D87"


def gen_simple_hitter(career_df, primary_colour=PRIMARY_COLOUR):
    """Function to generate a simple plotly visualization"""

    # Grab season total / average
    viz_df = career_df[
        (career_df["team_logo"] == "null") | (career_df["num_teams"] == 1)
    ].reset_index(drop=True)
    viz_df["avg"] = viz_df["avg"].astype(float)

    # Create figure
    fig = go.Figure()

    # Add data to figure
    fig.add_trace(
        go.Scatter(
            x=viz_df["season"],
            y=viz_df["avg"],
            marker={"color": primary_colour, "size": 10},
            line={"color": primary_colour, "dash": "dash"},
            hovertemplate="%{text}<extra></extra>",
            text=[
                f"Season: {viz_df.loc[idx, 'season']}<br>"
                f"Team: {viz_df.loc[idx, 'team_name']}<br>"
                f"Games Played: {viz_df.loc[idx, 'games']}<br>"
                f"Avg: {viz_df.loc[idx, 'avg']:.3f}<br>"
                f"RBI: {viz_df.loc[idx, 'rbi']}<br>"
                f"SB: {viz_df.loc[idx, 'stolen_bases']}<br>"
                f"BB: {viz_df.loc[idx, 'bb']}<br>"
                f"SO: {viz_df.loc[idx, 'strikeouts']}<br>"
                f"OPS: {viz_df.loc[idx, 'ops']}"
                for idx in range(viz_df["season"].count())
            ],
        )
    )

    # Update figure layout
    fig.update_layout(
        autosize=False,
        width=1200,
        title={
            "text": "<b>Season-By-Season Visualization</b>",
            "x": 0.5,
            "y": 0.9,
        },
        xaxis={"title": "Season"},
        yaxis={"title": "Hitting Average", "tickformat": ".3f"},
        font={
            "family": "sans-serif",
        },
    )

    return fig.to_html(include_plotlyjs="cdn", full_html=False)


def gen_simple_pitcher(career_df, primary_colour=PRIMARY_COLOUR):
    """Function to generate a simple plotly visualization"""

    # Grab season total / average
    viz_df = career_df[
        (career_df["team_logo"] == "null") | (career_df["num_teams"] == 1)
    ].reset_index(drop=True)
    viz_df["era"] = viz_df["era"].astype(float)

    # Create figure
    fig = go.Figure()

    # Add data to figure
    fig.add_trace(
        go.Scatter(
            x=viz_df["season"],
            y=viz_df["era"],
            marker={"color": primary_colour, "size": 10},
            line={"color": primary_colour, "dash": "dash"},
            hovertemplate="%{text}<extra></extra>",
            text=[
                f"Season: {viz_df.loc[idx, 'season']}<br>"
                f"Team: {viz_df.loc[idx, 'team_name']}<br>"
                f"Games Played: {viz_df.loc[idx, 'games']}<br>"
                f"Innings Pitched: {viz_df.loc[idx, 'ip']}<br>"
                f"Record (W-L): {viz_df.loc[idx, 'wins']}-{viz_df.loc[idx, 'losses']}<br>"
                f"Saves: {viz_df.loc[idx, 'saves']}<br>"
                f"ERA: {viz_df.loc[idx, 'era']:.2f}<br>"
                f"WHIP: {viz_df.loc[idx, 'whip']}<br>"
                f"SO: {viz_df.loc[idx, 'strikeouts']}<br>"
                f"BB: {viz_df.loc[idx, 'bb']}<br>"
                f"HR/9: {viz_df.loc[idx, 'hr_per_9']}"
                for idx in range(viz_df["season"].count())
            ],
        )
    )

    # Update figure layout
    fig.update_layout(
        autosize=False,
        width=1200,
        title={
            "text": "<b>Season-By-Season Visualization</b>",
            "x": 0.5,
            "y": 0.9,
        },
        xaxis={"title": "Season"},
        yaxis={"title": "Earned Run Average", "tickformat": ".2f"},
        font={
            "family": "sans-serif",
        },
    )

    return fig.to_html(include_plotlyjs="cdn", full_html=False)
