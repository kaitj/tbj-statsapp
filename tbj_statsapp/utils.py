def rank_map(rank):
    if rank > 3:
        return f"{rank}th"
    elif rank == 3:
        return f"{rank}rd"
    elif rank == 2:
        return f"{rank}nd"
    elif rank == 1:
        return f"{rank}st"
    else:
        raise ValueError("Invalid rank")
