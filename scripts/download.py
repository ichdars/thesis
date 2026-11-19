from gbd import *
from logs import *
import polars as pl

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


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument("--log", type=Path)
    parser.add_argument("--path", type=Path)

    args = parser.parse_args()

    log_data = parse_path(args.path)

    print(log_data)

    print(compare_names(log_data, load_data_frame()))
