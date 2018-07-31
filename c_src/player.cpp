#include "player.h"
#include <algorithm>

template< typename T, typename Pred >
typename std::vector<T>::iterator
    insert_sorted( std::vector<T> & vec, T const& item, Pred pred )
{
    return vec.insert
        ( 
           std::upper_bound( vec.begin(), vec.end(), item, pred ),
           item 
        );
}

Player::Player(const vector<TILE_TYPE>& tiles) {
    this->add(tiles);
}

void Player::add(const vector<TILE_TYPE>& tiles) {
    for (const auto& t : tiles) {
        this->cnt[static_cast<int>(t)]++;
        insert_sorted(this->tiles, t, [](const TILE_TYPE& t1, const TILE_TYPE& t2) {
            return static_cast<int>(t1) < static_cast<int>(t2);
        });
    }
}

void Player::remove(const vector<TILE_TYPE>& tiles) {
    for (const auto& t : tiles) {
        this->cnt[static_cast<int>(t)]--;
        auto pr = std::equal_range(std::begin(this->tiles), std::end(this->tiles), t);
        this->tiles.erase(pr.first, pr.second);
    }
}

bool Player::can_complete(const TILE_TYPE& tile) {
    if (tile != TILE_TYPE::NONE) {
        cnt[static_cast<int>(tile)]++;
    }
    bool b = false;
    int x = 0, p = -1;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 9; j++) {
            if (cnt[i * 9 + j] == 0 && b) {
                b = false;
                x |= 0x1 << p;
                p++;
            } else {
                p++;
                b = true;
                if (cnt[i * 9 + j] == 2) {
                    x |= 0x3 << p;
                    p += 2;
                } else if (cnt[i * 9 + j] == 3) {
                    x |= 0xf << p;
                    p += 4;
                } else if (cnt[i * 9 + j] == 4) {
                    x |= 0x3f << p;
                    p += 6;
                }
            }
        }
        if (b) {
            b = false;
            x |= 0x1 << p;
            p++;
        }
    }
    for (int i = 27; i < 34; i++) {
        if (cnt[i] > 0) {
            p++;
            if (cnt[i] == 2) {
                x |= 0x3 << p;
                p += 2;
            } else if (cnt[i] == 3) {
                x |= 0xf << p;
                p += 4;
            } else if (cnt[i] == 4) {
                x |= 0x3f << p;
                p += 6;
            }
            x |= 0x1 << p;
            p++;
        }
    }




    if (tile != TILE_TYPE::NONE) {
        cnt[static_cast<int>(tile)]--;
    }
}

bool Player::can_chow(const TILE_TYPE& tile, vector<vector<TILE_TYPE>>& sols) {
    if (tile == TILE_TYPE::NONE) {
        return false;
    }

    vector<vector<int>> arr = {{-2, -1}, {-1, 1}, {1, 2}};
    bool can = false;
    for (int bounds = 9; bounds <= 27; bounds += 9) {
        if (static_cast<int>(tile) >= bounds - 9 && static_cast<int>(tile) < bounds) {
            for (int i = 0; i < 3; i++) {
                auto val_before = static_cast<int>(tile) + arr[i][0];
                auto val_after = static_cast<int>(tile) + arr[i][1];
                if (val_before >= bounds - 9 && val_after < bounds && cnt[val_before] >= 1 && cnt[val_after] >= 1) {
                    can = true;
                    sols.push_back({static_cast<TILE_TYPE>(val_before), static_cast<TILE_TYPE>(val_after)});
                }
            }
        }
    }
    return can;
}

bool Player::can_pung(const TILE_TYPE& tile) {
    return cnt[static_cast<int>(tile)] >= 2;
}