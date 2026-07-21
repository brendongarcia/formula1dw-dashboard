import pandas as pd

from style import format_millis


def compute_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """df: columns DriverName, BestLapMillis. Returns ranked, formatted table."""
    out = df.sort_values("BestLapMillis", ascending=True, kind="stable").reset_index(drop=True)
    out["Rank"] = out.index + 1
    leader_ms = out["BestLapMillis"].iloc[0]
    out["BestLap"] = out["BestLapMillis"].apply(format_millis)
    out["Gap"] = out["BestLapMillis"].apply(
        lambda ms: "—" if ms == leader_ms else f"+{format_millis(ms - leader_ms)}"
    )
    return out[["Rank", "DriverName", "BestLap", "Gap"]]
