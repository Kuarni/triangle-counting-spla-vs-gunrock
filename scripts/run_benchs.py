import os
import subprocess
from pathlib import Path

iterations = 30

os_postfix = ".exe" if os.name == "nt" else ""
graphs_dir = Path("graphs")


def get_bench_exe(name):
    path = Path(f"bin/{name}-measure" + os_postfix)
    assert path.exists()
    return path


def bench(name):
    params = [f"--benchmark_out=results/{name}_bench_result.json", "--benchmark_out_format=json",
              f"--benchmark_repetitions={iterations}"]
    graphs = [f for f in graphs_dir.iterdir() if f.is_file()]
    graphs_for_bench = [str(fi.absolute()) for fi in graphs]
    cmd = subprocess.run([str(get_bench_exe(name)), *params, "--graphs", *graphs_for_bench])
    print(" ".join(cmd.args))


def bench_all():
    bench("spla")
    bench("gunrock")


if (__name__ == "__main__"):
    bench_all()
