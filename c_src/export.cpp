#include "mctree.h"

PYBIND11_MODULE(clib, m) {
    py::class_<State> s(m, "State");
    s.def(py::init<int, int, const vector<TILE_TYPE>&, int>());
    py::enum_<TILE_TYPE>(m, "TILE_TYPE")
        .value("BAMBOO_ONE", TILE_TYPE::BAMBOO_ONE)
        .value("BAMBOO_TWO", TILE_TYPE::BAMBOO_TWO)
        .value("BAMBOO_THREE", TILE_TYPE::BAMBOO_THREE)
        .value("BAMBOO_FOUR", TILE_TYPE::BAMBOO_FOUR);
    py::enum_<STATE_ID>(m, "STATE_ID")
        .value("CHOW", STATE_ID::CHOW)
        .value("DISCARD", STATE_ID::DISCARD)
        .value("PUNG1", STATE_ID::PUNG1)
        .value("PUNG2", STATE_ID::PUNG2)
        .value("PUNG3", STATE_ID::PUNG3);
}