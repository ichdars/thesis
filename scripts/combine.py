from pathlib import Path
import pandas as pd

from logs import parse_path

def merge(log_data: Path, cnfstats_gbd: str | Path):

    logs_df = pd.DataFrame(parse_path(log_data))
    logs_df.columns = [c.replace(" ", "_") for c in logs_df.columns]

    gbd_df = pd.read_csv(cnfstats_gbd)

    merged = logs_df.merge(
        gbd_df,
        on="benchmark",
        how="outer",
        indicator=True,
        validate="many_to_one",        
    )

    return merged
