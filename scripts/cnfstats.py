from pathlib import Path
import subprocess
import pandas as pd

CNF_SCRIPT = str(Path(__file__).resolve().parent.parent.parent / "cnfstats" / "cnfstats")
SUFFIXES = (".xz", ".gz", ".bz2", ".cnf")
CNF_KEYS = {
    "variables": int,
    "clauses": int,
    "clause-variable-ratio": float,
    "bytes": int,
    "lines": int,
    "literals": int,
    "clashing": int,
    "duplicated": int,
    "maximum-literal-occurrence": int,
    "maximum-variable-occurrence": int,
    "average-size": float,
    "sum-of-size-squares": int,
}

KEYS_WITH_COUNT = {"smallest-size": (int, int), "largest-size": (int, int), "median-size": (float, float)}

PREFIX_TO_SKIP = ("sizes[", "log10[", "cnf")


def cut_suffix(path: Path):

    name = Path(path).name

    for suffix in SUFFIXES:
        name = name.removesuffix(suffix)
    return name


def stats_from_cnf(cnf: Path, binary: str = CNF_SCRIPT, timeout=None):

    process = subprocess.run(
        [binary, str(cnf)],
        capture_output=True,
        text=True,
        timeout=timeout
    )

    if process.returncode != 0:
        raise RuntimeError(
            f"cnfstats failed on {cnf} (exit {process.returncode})"
            )
    return process.stdout


def cnf_stats_to_dict(cnf_stats: str, prefix: str="cnfstats") -> dict:

    stats: dict = {}

    for line in cnf_stats.splitlines():
        vals = line.split()

        if not vals:
            continue

        if vals[0] != prefix or len(vals) < 3:
            raise ValueError(f"uncommon line: {line}")
        key, val = vals[1], vals[2:]

        if key in "version":
            stats[key] = "".join(val)

        elif key in CNF_KEYS:
            stats[key] = CNF_KEYS[key](val[0])

        elif key in KEYS_WITH_COUNT:
            val_type, counter_type = KEYS_WITH_COUNT[key]

            if len(val) < 2:
                raise ValueError(f"missing count for {key!r}: {line!r}")

            stats[key] = val_type(val[0])
            stats[f"{key}-count"] = counter_type(val[1].lstrip("#"))

        elif key.startswith(PREFIX_TO_SKIP):
            continue

        else:
            raise ValueError(f"unkown stat: {val}")

    return stats


def stats_from_suite(track: str, instance_dir: Path, out_dir, families: dict[str, str] | None = None ,binary=CNF_SCRIPT) -> pd.DataFrame:

    out_dir = Path(out_dir)
    track_dir = out_dir / track
    out_folder = track_dir / "out"
    err_folder = track_dir / "err"

    out_folder.mkdir(parents=True, exist_ok=True)
    err_folder.mkdir(parents=True, exist_ok=True)

    instances = sorted(cnf for cnf in Path(instance_dir).iterdir() if cnf.is_file())

    names = [cut_suffix(name) for name in instances]
    duplicates = {dup for dup in names if names.count(dup) > 1}

    if duplicates:
        raise ValueError(f"benchmark nams not unique: {sorted(duplicates)}")

    rows = []

    for instance, name in zip(instances, names):
        out_file = out_folder / f"{name}.out"
        err_file = err_folder / f"{name}.err"

        if not out_file.exists():
            try:
                out_file.write_text(stats_from_cnf(instance, binary=binary), encoding="utf-8")

            except (RuntimeError, subprocess.TimeoutExpired) as e:
                err_file.write_text(str(e) + "\n", encoding="utf-8")
                print(f"error: {name}: {e}")

        if out_file.exists():
            row = {"status" : "ok", **cnf_stats_to_dict(out_file.read_text(encoding="utf-8"))}
        else:
            row = {"status": "error"}
        rows.append({"benchmark": name, "family": (families or {}).get(name) ,**row})

    df = pd.DataFrame(rows)

    df.columns = [c if c in ("benchmark", "family") else "cs_" + c.replace("-", "_") for c in df.columns]

    df.to_csv(track_dir / "cnfstats.csv", index=False)

    return df
