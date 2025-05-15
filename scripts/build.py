import subprocess
import os

def build():
    extra_options = ["-DCMAKE_BUILD_TYPE=Release", "-DENABLE_GUNROCK=OFF"]

    if (os.name == "nt"):
        extra_options.append("-G Visual Studio 17 2022")

    subprocess.run(["cmake", "-S .", "-B build", *extra_options])
    subprocess.run(["cmake", "--build", "build", "--config", "Release"])
    subprocess.run(["cmake", "--install", "build", "--prefix", "bin"])

if (__name__ == "__main__"):
    build()
