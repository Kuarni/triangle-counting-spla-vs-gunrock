import os
import subprocess
import sys
from pathlib import Path

iterations = 30

os_postfix = ".exe" if os.name == "nt" else ""
graphs_dir = Path("graphs")

predefines = {
    "spla_intel_opencl": ["--platform", "2", "--extra-name", "INTEL_OPENCL_RUNTIME_"]
}


def get_bench_exe(name):
    if name == "spla_intel_opencl": name = "spla"
    path = Path(f"bin/{name}-measure" + os_postfix)
    assert path.exists(), path
    return path


def bench(name):
    params = []
    if name in predefines.keys():
        params = predefines[name]

    params += [f"--benchmark_out=results/{name}_bench_result.json", "--benchmark_out_format=json",
               f"--benchmark_repetitions={iterations}"]
    graphs = [f for f in graphs_dir.iterdir() if f.is_file()]
    graphs_for_bench = [str(fi.absolute()) for fi in graphs]
    cmd = subprocess.run([str(get_bench_exe(name)), *params, "--graphs", *graphs_for_bench])
    print(" ".join(cmd.args))


if (__name__ == "__main__"):
    for i in sys.argv[1:]:
        bench(i)
