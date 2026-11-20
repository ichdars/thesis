from pathlib import Path
import subprocess

CNF_SCRIPT = str(Path(__file__).resolve().parent.parent.parent / "cnfstats" / "cnfstats")

def get_cnfstats(cnf: Path, binary: str=CNF_SCRIPT, timeout=None):

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
