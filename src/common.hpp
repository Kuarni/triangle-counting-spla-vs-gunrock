#pragma once

#include <filesystem>
#include <fstream>
#include <optional>

static std::optional<std::filesystem::path> lastLoadMatrixPath;
using matrix_as_vector = std::vector<std::pair<int, int>>;
using load_matrix_res = std::tuple<matrix_as_vector, int, int>;
static std::optional<load_matrix_res> lastLoadMatrixResult;

inline load_matrix_res loadMatrixAsVector(std::filesystem::path path) {
  if (lastLoadMatrixPath && lastLoadMatrixPath.value() == path) {
    return *lastLoadMatrixResult;
  }
  auto fstream = std::ifstream{path};
  auto data = std::vector<std::pair<int, int>>{};
  auto maxRow = 0;
  auto maxCol = 0;
  while (!fstream.eof()) {
    if (fstream.peek() == '#') {
      fstream.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
      continue;
    }
    int row, col;
    fstream >> row >> col;
    maxRow = std::max(maxRow, row);
    maxCol = std::max(maxCol, col);
    data.emplace_back(row, col);
  }
  lastLoadMatrixPath = path;
  lastLoadMatrixResult.emplace(data, maxRow, maxCol);
  return *lastLoadMatrixResult;
}

inline auto parseGraphPaths(int argc, char **argv) {
  std::string paramName = "--graphs";
  auto graphStarts = false;
  auto graphPaths = std::vector<std::filesystem::path>{};
  for (int i = 1; i < argc; i++) {
    if (graphStarts) {
      graphPaths.emplace_back(argv[i]);
    } else {
      graphStarts = paramName == argv[i];
    }
  }

  if (graphStarts && graphPaths.empty())
    throw std::invalid_argument("Zero graphs were passed");
  return graphPaths;
}

template <typename Fun>
void registerBenchmark(const std::string prefix, Fun fun,
                       std::filesystem::path graphPath) {
  auto name = prefix + graphPath.filename().string();
  benchmark::RegisterBenchmark(name, fun, graphPath)->Iterations(1);
}
