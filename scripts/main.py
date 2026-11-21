from argparse import ArgumentParser
from gbd import *
from download import *
from cnfstats import *
from logs import *
from combine import merge


def build_parser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument("--logs", type=Path)
    parser.add_argument("--track", type=str)

    return parser


def run(logs: Path, track: str):

    data_dir = Path(__file__).resolve().parent.parent / "data"

    instance_dir = data_dir / "gbd_instances" / track
    stats_dir = data_dir / "cnfstats"
    csv_dir = stats_dir / track /"cnfstats.csv"

    casted_df, _ = load_data_frame(track=track)

    download(casted_df, instance_dir)

    names = [cut_suffix(file) for file in casted_df["filename"].to_list()]
    families = dict(zip(names, casted_df["family"]))
    df = stats_from_suite(track=track, instance_dir=instance_dir, out_dir=stats_dir, families=families)

    merged_df: pd.DataFrame = merge(logs, csv_dir)

    print(merged_df["_merge"].value_counts())

    return merged_df


if __name__ == "__main__":

    parser: ArgumentParser = build_parser()
    args = parser.parse_args()

    print(run(args.logs, args.track))
