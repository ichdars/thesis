from argparse import ArgumentParser
from gbd import *
from download import *
from cnfstats import *
from logs import *
from combine import merge


def build_parser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument("--log", type=Path)
    parser.add_argument("--logs", type=Path)
    parser.add_argument("--cnf", type=Path)
    parser.add_argument("--gbd", type=Path)
    parser.add_argument("--csv", type=Path)

    return parser


if __name__ == "__main__":

    parser: ArgumentParser = build_parser()
    args = parser.parse_args()


    print(merge(args.logs, args.csv))


    # stats_from_suite("main_2024", args.gbd, "../data/cnfstats")

    # stats_from_cnf(args.cnf)