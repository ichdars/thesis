import matplotlib.pyplot as plt
import numpy as np
from argparse import ArgumentParser
from pathlib import Path
import pandas as pd


def load_combined(csv: Path) -> pd.DataFrame:
    if not csv.exists():
        raise FileNotFoundError(f"{csv} does not exist - run main.py first")
    return pd.read_csv(csv, dtype={"benchmark": str})


def family_plot(data: pd.DataFrame, solver: str, min_fams: int = 5, time_limit: float = 5000):

    data = data[data["solver"] == solver]

    family_count = data["family"].value_counts()
    fams_to_keep = family_count[family_count >= min_fams].index
    data = data[data["family"].isin(fams_to_keep)]

    order = data.groupby("family")["real_time"].median().sort_values().index

    fig, ax = plt.subplots(figsize=(14, 6))
    rng = np.random.default_rng(0)

    for index, family in enumerate(order):

        group = data[data["family"] == family]
        sat = group[group["status"] == "SATISFIABLE"]
        unsat = group[group["status"] == "UNSATISFIABLE"]
        unknown = group[group["status"] == "UNKNOWN"]

        x_sat = index + rng.uniform(-0.3, 0.3, size=len(sat))
        x_unsat = index + rng.uniform(-0.3, 0.3, size=len(unsat))
        x_unknown = index + rng.uniform(-0.3, 0.3, size=len(unknown))

        
        ax.scatter(x_sat, sat["real_time"], marker="^", s=14, alpha=0.6, color="tab:green", label="SAT" if index == 0 else None)
        ax.scatter(x_unsat, unsat["real_time"], marker="o", s=14, alpha=0.6, color="tab:red", label="UNSAT" if index == 0 else None)
        ax.scatter(x_unknown, unknown["real_time"], marker="x", s=14, alpha=0.6, color="tab:purple", label="UNKNOWN" if index == 0 else None)
        
        ax.hlines(y=group["real_time"].median(), xmin=index - 0.35, xmax=index + 0.35, color="black", linewidth=2)
 
    ax.axhline(time_limit, linestyle="--", color="gray", linewidth=1)
    ax.set_yscale("log")

    ax.set_xticks(range(len(order)), labels=[f"{f} (n={family_count[f]})" for f in order], rotation=60, ha="right")

    ax.set_ylabel("Runtime (Real Time) [s]")
    ax.set_xlabel("Family")
    ax.set_title(f"{solver}: runtime per family (families with n >= {min_fams})")

    ax.legend()

    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    return fig


if __name__ == "__main__": 
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--o", type=Path, help="Directory to save the plot")
    parser.add_argument("--solver", type=str, default="cadical")
    args = parser.parse_args()

    df = load_combined(args.csv)
    plot = family_plot(df, args.solver)

    if args.o is not None:
        args.o.mkdir(parents=True, exist_ok=True)
        plot.savefig(args.o / f"runtime_family_{args.solver}.pdf", bbox_inches="tight")
    else:
        plt.show()
