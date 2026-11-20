from pathlib import Path
from argparse import ArgumentParser
import re

SOLVER_FLAG = re.compile(r"^c (\S+) SAT Solver")


FIELDS = {

    (r"c run\.sh: benchmark",  "benchmark",    lambda x : x.split()[-1]),
    ("c total process time",   "process time", lambda x: float(x.split()[-2])), 
    ("c total real time",      "real time",    lambda x: float(x.split()[-2])),
    (r"c \S+ SAT Solver",      "solver",       lambda x: x.split()[1].lower())

}


def read_log(log: Path) -> dict[str, str | float]:

    res: dict[str, str | float] = {}

    with log.open(encoding="utf-8", errors="replace") as f:

        for line in f:

            line = line.strip()

            for flag, attr, evaluate in FIELDS:
                if re.match(flag, line):
                    res[attr] = evaluate(line)
    return res


def parse_path(folder: Path) -> list[dict[str, float |str]]:

    res: list[dict[str, str | float]] = []

    p = Path(folder)
    logs = p.glob("*.log")

    for log in logs:
        res.append(read_log(log))
    return res
