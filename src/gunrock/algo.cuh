#pragma once

void loadGunrockGraph(std::vector<std::pair<int, int>> edges, int maxRow,
                      int maxCol);

size_t runTriangleCountingCuda();

void cleanupGunrockResources();

