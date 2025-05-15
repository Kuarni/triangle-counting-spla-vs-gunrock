import os
import subprocess
from pathlib import Path

iterations = 30

os_postfix = ".exe" if os.name == "nt" else ""
graphs_dir = Path("graphs")
benchExe = Path("bin/spla-measure" + os_postfix)
params = ["--benchmark_out=results/spla_bench_result.json", "--benchmark_out_format=json",
          f"--benchmark_repetitions={iterations}"]


def bench():
    graphs = [f for f in graphs_dir.iterdir() if f.is_file()]
    graphs_for_bench = [str(fi.absolute()) for fi in graphs]
    cmd = subprocess.run([str(benchExe), *params, "--graphs", *graphs_for_bench])
    print(" ".join(cmd.args))


if (__name__ == "__main__"):
    bench()
