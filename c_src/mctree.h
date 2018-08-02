#include <vector>

#include <iostream>
#include <fstream>

#include "player.h"
#include <thread>
#include <mutex>

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
    int winner = 10;
    STATE_ID id;
    vector<Player*> players;
    vector<TILE_TYPE>remain_cards;

    State(STATE_ID id, TILE_TYPE last_tile, 
        const vector<vector<TILE_TYPE>>& handcards, 
        const vector<TILE_TYPE>& deck, int idx);
    State(const State&);

    ~State();
    
    vector<vector<TILE_TYPE>> get_action_space();

};


class Edge;

class Node {
public:
    State* st = nullptr;
    vector<vector<TILE_TYPE>> actions;
    Edge* src = nullptr;
    vector<Edge*> edges;
    std::mutex mu;

    Node(Edge* src, State* st, vector<float> priors = vector<float>());

    ~Node();

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
    Node* src = nullptr;
    Node* dest = nullptr;

    Edge(Node* src, const vector<TILE_TYPE>& action, float prior);

    ~Edge();
};


class MCTree {
public:
    Node* root = nullptr;
    int idx = -1;
    int counter = 0;
    float c = 0;
    std::mutex counter_mu;

    MCTree(State*, int idx, float c);

    ~MCTree();

    void search(int n_threads, int n);
    void search_thread();
    Node* explore(Node* node, float& val);
    void backup(Node* node, float val);
    float rollout(Node* node);
    vector<TILE_TYPE> predict(float temp);
};


State* step(const State& s, const vector<TILE_TYPE>& a);