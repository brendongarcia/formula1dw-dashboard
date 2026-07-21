from sqlalchemy import text


def get_races_to_process(engine, schedule_df):
    with engine.connect() as conn:
        loaded = conn.execute(text("""
            SELECT DISTINCT r.Season, r.Round
            FROM dw.DimRace r
            INNER JOIN dw.FactResults fr ON fr.RaceKey = r.RaceKey
        """)).fetchall()

    loaded_set = {(row[0], row[1]) for row in loaded}
    all_races = {(int(s), int(r)) for s, r in zip(schedule_df["season"], schedule_df["round"])}

    missing = all_races - loaded_set
    to_process = set(missing)

    if loaded_set:
        latest_season, latest_round = max(loaded_set)
        if (latest_season, latest_round) in all_races:
            races_after_latest = {
                (season, round_) for season, round_ in missing
                if season == latest_season and round_ > latest_round
            }
            # ponytail: refresh the latest loaded race only while the pipeline
            # is caught up (at most one unprocessed race after it); once it's
            # 2+ races stale, the post-race correction window has passed.
            if len(races_after_latest) <= 1:
                to_process.add((latest_season, latest_round))

    return sorted(to_process)
