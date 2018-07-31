#include <vector>

#include <pybind11/pybind11.h>
#include <iostream>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "player.h"
#include <thread>
#include <mutex>

namespace py = pybind11;
using namespace pybind11::literals;
using namespace std;


enum class STATE_ID {
    CHOW = 0,
    DISCARD = 1,
    PUNG1 = 2,
    PUNG2 = 3,
    PUNG3 = 4,
    FINISHED = 5
};



class State {
public:
    TILE_TYPE last_tile;
    int idx = 0;
    int winner = -1;
    STATE_ID id;
    vector<Player*> players;
    vector<TILE_TYPE>remain_cards;
    State(STATE_ID id, TILE_TYPE last_tile, 
        const vector<TILE_TYPE>& handcards, 
        const vector<TILE_TYPE>& remain_cards, int idx);
    
    vector<vector<TILE_TYPE>> get_action_space();

};


class Edge;

class Node {
public:
    State* st;
    vector<vector<TILE_TYPE>> actions;
    Edge* src;
    vector<Edge*> edges;
    std::mutex mu;

    Node(Edge* src, State* st, vector<float> priors = vector<float>());
    Edge* choose(float c);
};


class Edge {
public:
    vector<TILE_TYPE> action;
    int n = 0;
    float w = 0.f;
    float q = 0.f;
    bool terminiated = false;
    std::mutex mu;
    float r = 0.f;
    float p = 0.f;
    Node* src;
    Node* dest;

    Edge(Node* src, const vector<TILE_TYPE>& action, float prior);
};


class MCTree {
public:
    Node* root;
    int idx;
    int counter = 0;
    std::mutex counter_mu;

    MCTree(State*, int idx);
    void search(int n_threads, int n);
    void search_thread();
    Node* explore(Node* node, float& val);
    void backup(Node* node, float val);
    float rollout(Node* node);
};


State* step(const State& s, const vector<TILE_TYPE>& a);