#include "mctree.h"
#include <assert.h>

State::State(STATE_ID id, TILE_TYPE last_tile, const vector<TILE_TYPE>& handcards,
        const vector<TILE_TYPE>& left_cards, int idx) {
    this->id = id;
    this->last_tile = last_tile;
    // TODO: random assign unseen cards to deck and players
    this->remain_cards = left_cards;
    this->idx = idx;
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

State* step(const State& s, const vector<TILE_TYPE>& a) {
    State* sprime = new State(s);

    if (sprime->id == STATE_ID::CHOW) {
        sprime->id = STATE_ID::DISCARD;
        if (a.size() > 0) {
            sprime->players[sprime->idx]->remove(a);
        } else {
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
        Node* leaf = explore(root, val);
        if (leaf) {
            
        }
    }
}

Node* MCTree::explore(Node* node, float& val) {
    std::unique_lock<std::mutex> lock(node->mu);
    auto edge = node->choose(1.f);
    if (edge->dest) {
        lock.unlock();
        if (edge->terminiated) {
            val = edge->r;
            return edge->dest;
        } else {
            return explore(edge->dest, val);
        }
    } else {
        State* sprime = step(*node->st, edge->action);
        edge->dest = new Node(edge, sprime);
        lock.unlock();
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
        val = rollout(edge->dest);
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
    return 0;
}