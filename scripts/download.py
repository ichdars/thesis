from gbd import *
from logs import *
import polars as pl
import requests

URL = "https://benchmark-database.de/file/{}?context=cnf"

def compare_names(log_data: list[dict[str, float | str]], df: pl.DataFrame) -> tuple[int, list[str]]:
    res: int = 0

    not_in_df: list[str] = []

    names = set(df["filename"].str.strip_suffix(".cnf.xz"))

    for file in log_data:
        if file["benchmark"] in names:
            res += 1
        else:
            not_in_df.append(str(file["benchmark"]))

    return res, not_in_df


def download(df, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for hash, name in df.select("hash", "filename").iter_rows():
        out = target / name

        if out.exists():
            continue

        tmp = out.with_suffix(out.suffix + ".part")

        with  requests.get(URL.format(hash), stream=True, timeout=60) as r:
            r.raise_for_status()
            with tmp.open("wb") as f:
                for chunk in r.iter_content(chunk_size= 1 << 20):
                    f.write(chunk)
        tmp.rename(out)
