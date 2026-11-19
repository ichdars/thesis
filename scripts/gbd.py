import re
from gbd_core.api import GBD
import polars as pl

COLS_TO_CHECK = ["hash", "family", "family"]


def validate(df: pl.DataFrame) -> None: 

    missing = [col for col in COLS_TO_CHECK if col not in df.columns]

    if missing != []:
        raise ValueError(f"Columns missing in DataFrame: {missing}")

    problems: list[str] = []

    surplus_rows = df.height - df["hash"].n_unique()

    if surplus_rows > 0:
        raise ValueError(f"{surplus_rows} rows share the same hash")

    for col in COLS_TO_CHECK:
        nulls = df[col].null_count()
        if nulls > 0:
            problems.append(f"{nulls} missing values in column {col}")
    
    if problems:
        raise ValueError("Invalid DataFrame: " + "; ".join(problems))

def cast_columns(df: pl.DataFrame) -> pl.DataFrame:
    numeric_cols = []
    text_cols = []

    for name, type in df.schema.items():
        if type != pl.String:
            continue
        cast = df[name].cast(pl.Float64, strict=False)
        if cast.null_count() == df[name].null_count():
            numeric_cols.append(name)
        else:
            text_cols.append(name)
    
    casted = df.with_columns(pl.col(numeric_cols).cast(pl.Float64))

    return casted 

def load_data_frame(dbs: list[str] = ['../data/meta.db','../data/base.db'], track: str = "main_2024", feats: list[str] | None = None) -> pl.DataFrame:
    
    with GBD(dbs) as gbd:

        db_name = re.search(r'([^/\\]+)\.db$', dbs[-1]).group(1) # type: ignore
        feat = gbd.get_features(db_name) + ['family'] + ['filename']

        if feats:
            feat += feats

        df = gbd.query(
            f"track = {track}",
            resolve=feat
        )

    casted = cast_columns(df)

    validate(casted)

    return casted


if __name__ == "__main__":
    df = load_data_frame()
    print(df)