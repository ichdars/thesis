from pathlib import Path
import pandas as pd

from logs import parse_path

def merge(log_data: Path, cnfstats_gbd: pd.DataFrame):

    logs_df = pd.DataFrame(parse_path(log_data))
    logs_df.columns = [c.replace(" ", "_") for c in logs_df.columns]

    dups = logs_df[logs_df.duplicated(["benchmark", "solver"], keep=False)]

    if not dups.empty:
        raise ValueError(f"multiple logs for the same becnhamrk: \n{dups[['benchmark', 'solver']]}")

    merged = logs_df.merge(
        cnfstats_gbd,
        on="benchmark",
        how="outer",
        indicator=True,
        validate="many_to_one",        
    )

    just_logs = merged.loc[merged["_merge"] == "left_only", "benchmark"].to_list()
    just_cnf = merged.loc[merged["_merge"] == "right_only", "benchmark"].to_list()

    if just_logs:
        print(f"{len(just_logs)} logfiles have no corresponding gbd-instancese.g.{just_logs[:3]}")

    if just_cnf:
        print(f"{len(just_cnf)} gbd-instances have no corresponding logfiles, e.g.{just_cnf[:3]}")


    return merged[merged["_merge"] == "both"].drop(columns="_merge")
