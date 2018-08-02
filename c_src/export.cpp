#include "mctree.h"
#include <unordered_set>

// #include <pybind11/numpy.h>
// #include <pybind11/stl.h>
// #include <pybind11/pybind11.h>

// namespace py = pybind11;
// using namespace pybind11::literals;
unordered_set<int> complete_keys;

vector<TILE_TYPE> mc_search(STATE_ID id, TILE_TYPE last_tile, vector<vector<TILE_TYPE>> handcards,
        vector<TILE_TYPE> deck, int current_idx, int control_idx, int n_threads, int n, float c = 1.f, float temp = 0.5f) {
    State* root = new State(id, last_tile, handcards, deck, current_idx);
    // cout << static_cast<int>(id) << endl;
    // cout << static_cast<int>(last_tile) << endl;
    // for (auto& hc : handcards) {
    //     for (auto c : hc) {
    //         cout << static_cast<int>(c) << ", ";
    //     }
    //     cout << endl;
    // }
    // for (auto c : deck) {
    //     cout << static_cast<int>(c) << ", ";
    // }
    // cout << endl;
    // cout << current_idx << endl << control_idx << endl << n_threads << endl << n << endl;
    
    MCTree tree(root, control_idx, c);
    tree.search(n_threads, n);
    auto res = tree.predict(temp);
    // for (auto r : res) {
    //     cout << static_cast<int>(r) << ", ";
    // }
    // cout << endl;
    return res;
}

int main() {
    // mc_search(STATE_ID::DISCARD, TILE_TYPE::NONE, {{TILE_TYPE::BAMBOO_ONE, TILE_TYPE::BAMBOO_ONE}, {TILE_TYPE::BAMBOO_ONE, TILE_TYPE::BAMBOO_ONE}, {TILE_TYPE::BAMBOO_ONE, TILE_TYPE::BAMBOO_ONE}},
    //     {TILE_TYPE::BAMBOO_ONE, TILE_TYPE::BAMBOO_ONE}, 0, 0, 4, 1000);
    // FILE f("../../complete.bin");
    // int values[9362];
    // fread(values, sizeof(int), 9362, )
    ifstream fs ("../../complete.bin", ios::in | ios::binary);
    
    if (fs.is_open()) {
        fs.seekg(0, ios::end);
        int f_size = fs.tellg();
        fs.seekg(0);
        vector<int> nums(f_size / sizeof(int), 0);
        fs.read((char*)&nums[0], f_size);
        cout << nums.size() << endl;
        for (auto i : nums) {
            complete_keys.insert(i);
        }
    } else {
        cout << "sth wrong." << endl;
    }
    Player p({TILE_TYPE::BAMBOO_ONE, TILE_TYPE::BAMBOO_ONE, TILE_TYPE::BAMBOO_ONE});
    cout << p.can_complete() << endl;
}

// PYBIND11_MODULE(clib, m) {
//     m.def("mc_search", &mc_search, py::arg("state_id"), py::arg("last_tile"),
//         py::arg("handcards"), py::arg("deck"),
//         py::arg("current_idx"), py::arg("control_idx"),
//         py::arg("n_threads"), py::arg("n"),
//         py::arg("c") = 1.f, py::arg("temp") = 0.5f);
//     py::enum_<TILE_TYPE>(m, "TILE_TYPE")
//         .value("BAMBOO_ONE", TILE_TYPE::BAMBOO_ONE)
//         .value("BAMBOO_TWO", TILE_TYPE::BAMBOO_TWO)
//         .value("BAMBOO_THREE", TILE_TYPE::BAMBOO_THREE)
//         .value("BAMBOO_FOUR", TILE_TYPE::BAMBOO_FOUR)
//         .value("BAMBOO_FIVE", TILE_TYPE::BAMBOO_FIVE)
//         .value("BAMBOO_SIX", TILE_TYPE::BAMBOO_SIX)
//         .value("BAMBOO_SEVEN", TILE_TYPE::BAMBOO_SEVEN)
//         .value("BAMBOO_EIGHT", TILE_TYPE::BAMBOO_EIGHT)
//         .value("BAMBOO_NINE", TILE_TYPE::BAMBOO_NINE)
//         .value("CIRCLE_ONE", TILE_TYPE::CIRCLE_ONE)
//         .value("CIRCLE_TWO", TILE_TYPE::CIRCLE_TWO)
//         .value("CIRCLE_THREE", TILE_TYPE::CIRCLE_THREE)
//         .value("CIRCLE_FOUR", TILE_TYPE::CIRCLE_FOUR)
//         .value("CIRCLE_FIVE", TILE_TYPE::CIRCLE_FIVE)
//         .value("CIRCLE_SIX", TILE_TYPE::CIRCLE_SIX)
//         .value("CIRCLE_SEVEN", TILE_TYPE::CIRCLE_SEVEN)
//         .value("CIRCLE_EIGHT", TILE_TYPE::CIRCLE_EIGHT)
//         .value("CIRCLE_NINE", TILE_TYPE::CIRCLE_NINE)
//         .value("WAN_ONE", TILE_TYPE::WAN_ONE)
//         .value("WAN_TWO", TILE_TYPE::WAN_TWO)
//         .value("WAN_THREE", TILE_TYPE::WAN_THREE)
//         .value("WAN_FOUR", TILE_TYPE::WAN_FOUR)
//         .value("WAN_FIVE", TILE_TYPE::WAN_FIVE)
//         .value("WAN_SIX", TILE_TYPE::WAN_SIX)
//         .value("WAN_SEVEN", TILE_TYPE::WAN_SEVEN)
//         .value("WAN_EIGHT", TILE_TYPE::WAN_EIGHT)
//         .value("WAN_NINE", TILE_TYPE::WAN_NINE)
//         .value("SPECIAL_RED_DRAGON", TILE_TYPE::SPECIAL_RED_DRAGON)
//         .value("SPECIAL_GREEN_DRAGON", TILE_TYPE::SPECIAL_GREEN_DRAGON)
//         .value("SPECIAL_WHITE_DRAGON", TILE_TYPE::SPECIAL_WHITE_DRAGON)
//         .value("SPECIAL_EAST", TILE_TYPE::SPECIAL_EAST)
//         .value("SPECIAL_SOUTH", TILE_TYPE::SPECIAL_SOUTH)
//         .value("SPECIAL_WEST", TILE_TYPE::SPECIAL_WEST)
//         .value("SPECIAL_NORTH", TILE_TYPE::SPECIAL_NORTH)
//         .value("NONE", TILE_TYPE::NONE);
//     py::enum_<STATE_ID>(m, "STATE_ID")
//         .value("CHOW", STATE_ID::CHOW)
//         .value("DISCARD", STATE_ID::DISCARD)
//         .value("PUNG1", STATE_ID::PUNG1)
//         .value("PUNG2", STATE_ID::PUNG2)
//         .value("PUNG3", STATE_ID::PUNG3);
// }