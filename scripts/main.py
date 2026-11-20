from argparse import ArgumentParser
from gbd import *
from download import *
from evaluate import *
from logs import *


def build_parser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument("--log", type=Path)
    parser.add_argument("--path", type=Path)
    parser.add_argument("--cnf", type=Path)

    return parser


if __name__ == "__main__":

    parser: ArgumentParser = build_parser()
    args = parser.parse_args()

    get_cnfstats(args.cnf)