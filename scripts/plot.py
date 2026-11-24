import matplotlib.pyplot as plt
import numpy as np
from argparse import ArgumentParser
from pathlib import Path
import pandas as pd


def load_combined(csv: Path) -> pd.DataFrame:
    if not csv.exists():
        raise FileNotFoundError(f"{csv} does not exist - run main.py first")
    return pd.read_csv(csv, dtype={"benchmark": str})


def prepare(data: pd.DataFrame, solver: str, min_size: int):

    data = data[data["solver"] == solver]

    family_count = data["family"].value_counts()
    fams_to_keep = family_count[family_count >= min_size].index
    return data[data["family"].isin(fams_to_keep)], family_count


def family_to_realtime_plot(data: pd.DataFrame, solver: str, min_fams: int = 5, time_limit: float = 5000):

    data, family_count = prepare(data, solver=solver, min_size=min_fams)

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


def family_to_size_plot(data: pd.DataFrame, solver: str, min_fams: int = 5, size_stat: str = "cs_clauses", time_limit: int = 5000):

    data, fam_count = prepare(data, solver=solver, min_size=min_fams)
    data = data.dropna(subset=[size_stat])

    families = data.groupby("family")["real_time"].median().sort_values().index

    colors = plt.get_cmap("tab10").colors # type: ignore
    markers = ["o", "s"]

    fig, ax = plt.subplots(figsize=(12, 7))

    for index, family in enumerate(families):

        group = data[data["family"] == family ]
        sat = group[group["status"] == "SATISFIABLE" ]
        unsat = group[group["status"] == "UNSATISFIABLE" ]
        unknown = group[group["status"] == "UNKNWON"]

        color = colors[index % 10]
        marker = markers[index // 10 % 2]

        ax.scatter(sat[size_stat], sat["real_time"], marker=marker, s=22, color=color, alpha=0.8, zorder=3, label=f"{family} (n={fam_count[family]})")
        ax.scatter(unsat[size_stat], unsat["real_time"], marker=marker, s=22, facecolor="none", edgecolors=color, zorder=3)
        ax.scatter(unknown[size_stat], unknown["real_time"], marker=marker, s=22, facecolor="none", edgecolors=color, zorder=3)
        
    ax.axhline(time_limit, linestyle="--", color="grey", linewidth=1)

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel("Clauses (GBD instance)")
    ax.set_ylabel("Runtime (Real Time) [s]")

    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8, title="family (hollow = timeout)", title_fontsize=8)
    ax.grid(alpha=0.3)

    fig.tight_layout()

    return fig


def stat_box_plot(data: pd.DataFrame, solver: str, time_limit: int = 5000, min_fams: int = 5, stat: str = "cs_bytes", x_label: str = "Bytes (from GBD cnf)"):

    data = data[data["solver"] == solver].dropna(subset=[stat])

    low = int(np.floor(np.log10(data[stat].min())))
    high = int(np.ceil(np.log10(data[stat].max())))
    edges = 10.0 ** np.arange(low, high + 1)
    data = data.assign(bin=pd.cut(data[stat], edges, right=False)) # type: ignore   
    bins = data["bin"].cat.categories
    groups = [data[data["bin"] == b] for b in bins]

    fig, ax = plt.subplots(figsize=(10, 6))
    rng = np.random.default_rng(0)

    ax.boxplot([group["real_time"] for group in groups], positions=range(len(bins)), widths=0.6, showfliers=False)

    for index, group in enumerate(groups):
        x = index + rng.uniform(-0.25, 0.25, size=len(group))
        sat = (group["status"] == "SATISFIABLE").to_numpy()
        unsat = (group["status"] == "UNSATISFIABLE").to_numpy()
        unknown = (group["status"] == "UNKNOWN").to_numpy()

        ax.scatter(x[sat], group["real_time"][sat], marker="^", s=10, alpha=0.6, color="tab:green", zorder=3, label="SAT" if index == 0 else None)
        ax.scatter(x[unsat], group["real_time"][unsat], marker="o", s=10, alpha=0.6, color="tab:red", zorder=3, label="UNSAT" if index == 0 else None)
        ax.scatter(x[unknown], group["real_time"][unknown], marker="x", s=10, alpha=0.6, color="tab:purple", zorder=3, label="UNKNOWN" if index == 0 else None)
    
    
    ax.axhline(time_limit, linestyle="--", color="grey", linewidth=1)
    ax.set_yscale("log")
    labels = [f"$10^{{{int(np.log10(b.left))}}}$–$10^{{{int(np.log10(b.right))}}}$\n(n={len(g)})" for b, g in zip(bins, groups)]
    ax.set_xticks(range(len(bins)), labels=labels)

    ax.set_xlabel(x_label)
    ax.set_ylabel("Total Realtime [s]")
    ax.set_title(f"{solver}: runtime by {stat}")

    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    return fig 


if __name__ == "__main__": 
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--o", type=Path, help="Directory to save the plot")
    parser.add_argument("--solver", type=str, default="cadical")
    parser.add_argument("--stat", type=str, help="stat to do the boxplot with", default="cs_bytes")

    args = parser.parse_args()

    df = load_combined(args.csv)
    real_time_plot = family_to_realtime_plot(df, args.solver)
    family_size_plot = family_to_size_plot(df, args.solver)
    box_plot = stat_box_plot(df, args.solver, stat=args.stat)

    if args.o is not None:
        args.o.mkdir(parents=True, exist_ok=True)
        (args.o / "families").mkdir(parents=True, exist_ok=True)
        (args.o / "cnfstats").mkdir(parents=True, exist_ok=True)
        real_time_plot.savefig(args.o / "families" / f"runtime_family_{args.solver}.pdf", bbox_inches="tight")
        family_size_plot.savefig(args.o / "families" / f"family_size_{args.solver}.pdf", bbox_inches="tight")
        box_plot.savefig(args.o / "cnfstats" / f"bytes_boxplot_{args.solver}.pdf", bbox_inches="tight")
    else:
        plt.show()
