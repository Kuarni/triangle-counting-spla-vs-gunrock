#include "algo.cuh"

#define NOMINMAX

#include "algo.cuh"

#include <algorithm>
#include <filesystem>
#include <vector>

#include <gunrock/algorithms/tc.hxx>
#include <gunrock/formats/csr.hxx>
#include <gunrock/formats/formats.hxx>
#include <gunrock/graph/build.hxx>
#include <gunrock/graph/graph.hxx>
#include <gunrock/io/matrix_market.hxx>
#include <gunrock/memory.hxx>

using vertex_t = uint32_t;
using edge_t = uint32_t;
using weight_t = float;
using graph_t = gunrock::graph::graph_t<
    gunrock::memory::device, unsigned int, unsigned int, float,
    gunrock::graph::graph_csr_t<gunrock::memory::device, unsigned int,
                                unsigned int, float>>;

namespace {
std::optional<
    gunrock::format::csr_t<gunrock::memory::device, vertex_t, edge_t, weight_t>>
    g_csr;
std::optional<graph_t> g_graph;
thrust::device_vector<vertex_t> *g_triangles_count = nullptr;
bool g_initialized = false;
} // namespace

void loadGunrockGraph(std::vector<std::pair<int, int>> edges, int maxRow,
                      int maxCol) {
  using namespace gunrock;

  vertex_t V = std::max(maxRow, maxCol) + 1;

  std::set<std::pair<vertex_t, vertex_t>> unique_edges;

  for (auto [u, v] : edges) {
    if (u != v) {
      unique_edges.insert({u, v});
      unique_edges.insert({v, u});
    }
  }

  int E2 = unique_edges.size();

  std::vector<vertex_t> h_src, h_dst;
  std::vector<weight_t> h_w;

  for (auto [u, v] : unique_edges) {
    h_src.push_back(u);
    h_dst.push_back(v);
    h_w.push_back(1);
  }

  g_csr = format::csr_t<device, vertex_t, edge_t, weight_t>();
  format::coo_t<host, vertex_t, edge_t, weight_t> h_coo{
      V, V, static_cast<uint32_t>(E2)};

  h_coo.row_indices = h_src;
  h_coo.column_indices = h_dst;
  h_coo.nonzero_values = h_w;

  g_csr->from_coo(h_coo);

  gunrock::graph::graph_properties_t graph_properties{false, false, true};
  g_graph = gunrock::graph::build(graph_properties, *g_csr);

  g_triangles_count =
      new thrust::device_vector<vertex_t>(g_graph->get_number_of_vertices(), 0);

  g_initialized = true;
}

size_t runTriangleCountingCuda() {
  if (!g_initialized || !g_graph || !g_triangles_count) {
    throw std::runtime_error(
        "Graph not initialized before running triangle counting");
  }

  bool reduce_all_triangles = true;
  size_t total_triangles = 0;

  gunrock::tc::run(*g_graph, reduce_all_triangles,
                   g_triangles_count->data().get(), &total_triangles);

  return total_triangles / 3;
}

void cleanupGunrockResources() {
  g_graph.reset();
  g_csr.reset();

  if (g_triangles_count) {
    delete g_triangles_count;
    g_triangles_count = nullptr;
  }

  g_initialized = false;
}
