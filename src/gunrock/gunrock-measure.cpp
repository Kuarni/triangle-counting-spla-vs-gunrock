#define NOMINMAX

#include <benchmark/benchmark.h>
#include <filesystem>
#include <vector>

#include "algo.cuh"
#include "common.hpp"

static void bmGunrockTC(benchmark::State &state,
                        const std::filesystem::path &graphPath) {
  auto [data, maxRow, maxCol] = loadMatrixAsVector(graphPath);
  loadGunrockGraph(data, maxRow, maxCol);
  size_t result = 0;

  for (auto _ : state) {
    result = runTriangleCountingCuda();
  }

  state.counters["triangles"] = static_cast<double>(result);

  cleanupGunrockResources();
}

int main(int argc, char **argv) {
  auto graphPaths = parseGraphPaths(argc, argv);

  for (auto &path : graphPaths) {
    registerBenchmark("Gunrock_tc/", bmGunrockTC, path);
  }

  benchmark::Initialize(&argc, argv);
  benchmark::SetDefaultTimeUnit(benchmark::kMillisecond);
  benchmark::RunSpecifiedBenchmarks();

  return 0;
}
