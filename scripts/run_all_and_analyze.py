from analyze import *
from build import build
from download import download
from run_benchs import *

if __name__ == '__main__':
    download()
    build()
    bench("spla")
    bench("gunrock")
    analyze('results/spla_bench_result.json', 'results/gunrock_bench_result.json')
