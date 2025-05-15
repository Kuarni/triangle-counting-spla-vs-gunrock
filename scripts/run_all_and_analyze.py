from analyze import *
from build import build
from download import download
from run_benchs import *

if __name__ == '__main__':
    download()
    build()
    bench()
    analyze()
