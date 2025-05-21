#include <benchmark/benchmark.h>
#include <fstream>
#include <spla.hpp>
#include <string>
#include <utility>

#include "common.hpp"

void splaSetUp() {
  spla::Library *library = spla::Library::get();
  std::string acc_info;
  library->get_accelerator_info(acc_info);
  std::cout << "env: " << acc_info << std::endl;
  library->set_force_no_acceleration(false);
}

void splaTeardown() { spla::Library::get()->finalize(); }

auto loadGraph(std::filesystem::path path, bool trilingual = false) {
  auto [data, maxRow, maxCol] = loadMatrixAsVector(std::move(path));

  auto matrix = spla::Matrix::make(maxRow + 1, maxCol + 1, spla::INT);
  for (auto [row, col] : data) {
    if (row == col)
      continue;

    if (!trilingual) {
      matrix->set_int(row, col, 1);
      matrix->set_int(col, row, 1);
    } else {
      auto [i, j] = std::minmax(row, col);
      matrix->set_int(j, i, 1);
    }
  }
  matrix->set_format(spla::FormatMatrix::AccCsr);
  return matrix;
}

auto getMatrix(int n, int m) {
  auto matrix = spla::Matrix::make(n, m, spla::INT);
  matrix->set_format(spla::FormatMatrix::AccCsr);
  return matrix;
}

auto tcBurkhardt(int &ntrins, const spla::ref_ptr<spla::Matrix> &graph,
                 const spla::ref_ptr<spla::Matrix> &bufferMatrix) {
  using namespace spla;
  ref_ptr<Scalar> zero = Scalar::make_int(0);
  ref_ptr<Scalar> result = Scalar::make(INT);

  spla::exec_mxmT_masked(bufferMatrix, graph, graph, graph, MULT_INT, PLUS_INT,
                         GTZERO_INT, zero);
  spla::exec_m_reduce(result, zero, bufferMatrix, PLUS_INT);

  ntrins = result->as_int() / 6;
  return Status::Ok;
}

static void bmSplaSandia(benchmark::State &state,
                         const std::filesystem::path &graphPath) {
  using namespace spla;
  auto graph = loadGraph(graphPath, true);
  auto buffer = getMatrix(graph->get_n_rows(), graph->get_n_cols());
  int count = 0;
  Status status;

  for (auto _ : state) {
    status = tc(count, graph, buffer);
    benchmark::DoNotOptimize(status);
  }

  state.counters["triangles"] = count;
  state.counters["status"] = static_cast<int>(status);
}

static void bmSplaBurkhardt(benchmark::State &state,
                            const std::filesystem::path &graphPath) {
  using namespace spla;
  auto graph = loadGraph(graphPath);
  auto buffer = getMatrix(graph->get_n_rows(), graph->get_n_cols());
  int count = 0;
  Status status;

  for (auto _ : state) {
    status = tcBurkhardt(count, graph, buffer);
    benchmark::DoNotOptimize(status);
  }

  state.counters["triangles"] = count;
  state.counters["status"] = static_cast<int>(status);
}

int main(int argc, char **argv) {
  auto graphPaths = parseGraphPaths(argc, argv);

  for (auto &path : graphPaths) {
    registerBenchmark("SPLA_Burkhardt/", bmSplaBurkhardt, path);
    registerBenchmark("SPLA_Sandia/", bmSplaSandia, path);
  }

  splaSetUp();

  benchmark::Initialize(&argc, argv);
  benchmark::SetDefaultTimeUnit(benchmark::kMillisecond);
  benchmark::RunSpecifiedBenchmarks();

  splaTeardown();
  return 0;
}
