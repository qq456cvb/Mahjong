
#include <vector>
using namespace std;


enum class TILE_TYPE {
    BAMBOO_ONE = 0,
    BAMBOO_TWO = 1,
    BAMBOO_THREE = 2,
    BAMBOO_FOUR = 3,
    BAMBOO_FIVE = 4,
    NONE = 100
};

class Player {
    
    vector<int> cnt;

public:
    vector<TILE_TYPE> tiles;
    Player(const vector<TILE_TYPE>& tiles);
    void add(const vector<TILE_TYPE>& tiles);
    void remove(const vector<TILE_TYPE>& tiles);

    bool can_complete(const TILE_TYPE& tile = TILE_TYPE::NONE);
    bool can_chow(const TILE_TYPE& tile, vector<vector<TILE_TYPE>>& sols);
    bool can_pung(const TILE_TYPE& tile);
};

