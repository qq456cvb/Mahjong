#include "mctree.h"
#include <math.h>
#include <assert.h>
#include <unordered_set>

// unordered_set<int> complete_keys;

State::State(STATE_ID id, TILE_TYPE last_tile, const vector<vector<TILE_TYPE>>& handcards,
        const vector<TILE_TYPE>& deck, int idx) {
    this->id = id;
    this->last_tile = last_tile;
    for (int i = 0; i < handcards.size(); i++) {
        this->players.push_back(new Player(handcards[i]));
    }
    this->remain_cards = deck;
    this->idx = idx;
}

State::State(const State& s) : last_tile(s.last_tile), idx(s.idx), winner(s.winner), id(s.id), remain_cards(s.remain_cards) {
    for (int i = 0; i < s.players.size(); i++) {
        this->players.push_back(new Player(*s.players[i]));
    }
}

State::~State() {
    for (auto p : this->players) {
        if (p) {
            delete p;
        }
    }
}

vector<vector<TILE_TYPE>> State::get_action_space() {
    if (id == STATE_ID::CHOW) {
        vector<vector<TILE_TYPE>> sols = {{}};
        bool can_chow = players[idx]->can_chow(last_tile, sols);
        return sols;
    } else if (id == STATE_ID::DISCARD) {
        vector<vector<TILE_TYPE>> sols;
        for (const auto& t : players[idx]->tiles) {
            sols.push_back({t});
        }
        return sols;
    } else if (STATE_ID::PUNG1 <= id && id <= STATE_ID::PUNG3) {
        bool can_pung = players[(idx + 1 + static_cast<int>(id) - static_cast<int>(STATE_ID::PUNG1)) % 4]->can_pung(last_tile);
        vector<vector<TILE_TYPE>> sols = {{}};
        if (can_pung) {
            sols.push_back({last_tile, last_tile});
        }
        return sols;
    } else if (id == STATE_ID::FINISHED) {
        return {};
    } else {
        throw std::runtime_error("invalid state id");
    }
}


Node::Node(Edge* src, State* st, vector<float> priors) {
    this->st = st;
    this->actions = st->get_action_space();
    if (priors.empty() && !this->actions.empty()) {
        priors = vector<float>(this->actions.size(), 1.f / this->actions.size());
    }
    this->src = src;
    for (int i = 0; i < this->actions.size(); i++) {
        this->edges.push_back(new Edge(this, this->actions[i], priors[i]));
    }
}

Node::~Node() {
    if (this->st) {
        delete this->st;
    }
    for (auto e : this->edges) {
        if (e) {
            delete e;
        }
    }
}

Edge::Edge(Node* src, const vector<TILE_TYPE>& action, float prior) {
    this->action = action;
    this->p = prior;
    this->src = src;
}


Edge::~Edge() {
    if (this->dest) {
        delete this->dest;
    }
}


Edge* Node::choose(float c) {
    float sum = 0.f;
    for (auto e : edges) {
        sum += e->n;
    }
    float nsum_sqrt = sqrtf(sum);
    int best_idx = -1;
    float best = -100.f;
    for (int i = 0; i < edges.size(); i++) {
        float cand = edges[i]->q + c * edges[i]->p * nsum_sqrt / (1.f + edges[i]->n);
        if (cand > best) {
            best_idx = i;
            best = cand;
        }
    }
    return edges[best_idx];
}


MCTree::MCTree(State* st, int idx, float c) {
    // if (complete_keys.empty()) {
    //     ifstream fs ("./complete.bin", ios::in | ios::binary);
    //     if (fs.is_open()) {
    //         fs.seekg(0, ios::end);
    //         int f_size = fs.tellg();
    //         fs.seekg(0);
    //         vector<int> nums(f_size / sizeof(int), 0);
    //         fs.read((char*)&nums[0], f_size);
    //         cout << nums.size() << endl;
    //         for (auto i : nums) {
    //             complete_keys.insert(i);
    //         }
    //     } else {
    //         cout << "sth wrong." << endl;
    //     }
    // } else {
    //     // cout << "already exists" << endl;
    // }
    this->root = new Node(nullptr, st);
    this->idx = idx;
    this->counter = 0;
    this->c = c;
}


MCTree::~MCTree() {
    if (root) {
        delete root;
    }
}

void MCTree::search(int n_threads, int n) {
    counter = n;
    vector<thread> threads;
    for (int i = 0; i < n_threads; i++) {
        
        threads.push_back(std::move(std::thread(&MCTree::search_thread, this)));
    }
    for (auto& t : threads) {
        t.join();
    }
}

void MCTree::search_thread() {
    while (true) {
        {
            std::lock_guard<std::mutex> lock(counter_mu);
            if (counter == 0) {
                break;
            } else {
                counter--;
            }
        }
        float val = 0.f;
        // cout << "explore" << endl;
        Node* leaf = explore(root, val);
        // cout << val << endl;
        backup(leaf, val);
    }
}

Node* MCTree::explore(Node* node, float& val) {
    std::unique_lock<std::mutex> lock(node->mu);
    auto edge = node->choose(this->c);
    if (edge->dest) {
        
        if (edge->terminiated) {
            val = edge->r;
            lock.unlock();
            return edge->dest;
        } else {
            lock.unlock();
            return explore(edge->dest, val);
        }
    } else {
        // cout << node->st->idx << ": " << static_cast<int>(node->st->id) << ", ";
        // cout << node->st->get_action_space().size() << endl;
        State* sprime = step(*node->st, edge->action);
        while (sprime->idx != this->idx && sprime->id != STATE_ID::FINISHED) {
            auto last_s = sprime;
            auto actions = sprime->get_action_space();
            // cout << sprime->idx << ": " << static_cast<int>(sprime->id) << ", ";
            // cout << actions.size() << endl;
            sprime = step(*sprime, actions[rand() % actions.size()]);
            if (last_s) {
                delete last_s;
            }
        }
        edge->dest = new Node(edge, sprime);
        
        if (sprime->id == STATE_ID::FINISHED) {
            if (sprime->winner == idx) {
                edge->r = 1;
            } else if (sprime->winner >= 0) {
                edge->r = -1;
            } else {
                edge->r = 0;
            }
            edge->terminiated = true;
            val = edge->r;
            return edge->dest;
        }
        // cout << "rollout ";
        val = rollout(edge->dest);
        if (val != 0) {
            cout << val << ", ";
        }
        
        lock.unlock();
        return edge->dest;
    }
}

void MCTree::backup(Node* node, float val) {
    while (node->src) {
        auto edge = node->src;
        {
            std::lock_guard<std::mutex> lock(edge->mu);
            edge->n++;
            edge->w += val;
            edge->q = edge->w / edge->n;
        }
        node = edge->src;
    }
}

float MCTree::rollout(Node* node) {
    auto st = node->st;
    bool first_time = true;
    while (st->id != STATE_ID::FINISHED) {
        auto actions = st->get_action_space();
        // cout << st->idx << ": " << static_cast<int>(st->id) << ", ";
        // cout << actions.size() << endl;
        auto last_st = st;
        st = step(*st, actions[rand() % actions.size()]);
        if (!first_time) {
            delete last_st;
        }
        if (first_time) {
            first_time = false;
        }
    }
    float r = 0;
    cout << st->winner << endl;
    if (st->winner == idx) {
        r = 1.f;
    } else if (st->winner >= 0) {
        r = -1.f;
    } else {
        r = 0;
    }
    delete st;
    return r;
}

vector<TILE_TYPE> MCTree::predict(float temp) {
    int max_n = 0;
    int max_id = 0;
    for (int i = 0; i < root->edges.size(); i++) {
        // cout << root->edges[i]->q << ", ";
        if (root->edges[i]->n > max_n) {
            max_n = root->edges[i]->n;
            max_id = i;
        }
    }
    // cout << endl;
    return root->edges[max_id]->action;
}


State* step(const State& s, const vector<TILE_TYPE>& a) {
    State* sprime = new State(s);

    if (sprime->id == STATE_ID::CHOW) {
        sprime->id = STATE_ID::DISCARD;
        if (a.size() > 0) {
            assert(a.size() == 2);
            sprime->players[sprime->idx]->remove(a);
        } else {
            // cout << sprime->remain_cards.size() << endl;
            sprime->players[sprime->idx]->add({sprime->remain_cards.back()});
            sprime->remain_cards.pop_back();
            if (sprime->players[sprime->idx]->can_complete()) {
                sprime->id = STATE_ID::FINISHED;
                sprime->winner = sprime->idx;
            }
        }
    } else if (sprime->id == STATE_ID::DISCARD) {
        sprime->last_tile = a[0];
        sprime->players[sprime->idx]->remove(a);
        sprime->id = STATE_ID::PUNG1;
        for (int i = sprime->idx + 1; i < sprime->idx + 4; i++) {
            if (sprime->players[i % 4]->can_complete(sprime->last_tile)) {
                sprime->id = STATE_ID::FINISHED;
                sprime->winner = i % 4;
                break;
            }
        }
        if (sprime->remain_cards.empty() && sprime->id != STATE_ID::FINISHED) {
            sprime->id = STATE_ID::FINISHED;
            sprime->winner = -1;
        }
    } else if (STATE_ID::PUNG1 <= sprime->id && sprime->id <= STATE_ID::PUNG3) {
        if (a.size() > 0) {
            sprime->idx = (sprime->idx + 1 + static_cast<int>(sprime->id) - static_cast<int>(STATE_ID::PUNG1)) % 4;
            sprime->players[sprime->idx]->remove(a);
            sprime->id = STATE_ID::DISCARD;
        } else {
            if (sprime->id == STATE_ID::PUNG3) {
                sprime->idx = (sprime->idx + 1) % 4;
                sprime->id = STATE_ID::CHOW;
            } else {
                sprime->id = static_cast<STATE_ID>(static_cast<int>(sprime->id) + 1);
            }
        }
    }
    return sprime;
}
