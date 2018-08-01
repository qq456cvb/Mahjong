
#include <vector>
using namespace std;


enum class TILE_TYPE {
    BAMBOO_ONE = 0,
    BAMBOO_TWO = 1,
    BAMBOO_THREE = 2,
    BAMBOO_FOUR = 3,
    BAMBOO_FIVE = 4,
    BAMBOO_SIX = 5,
    BAMBOO_SEVEN = 6,
    BAMBOO_EIGEHT = 7,
    BAMBOO_NINE = 8,
    CIRCLE_ONE = 9,
    CIRCLE_TWO = 10,
    CIRCLE_THREE = 11,
    CIRCLE_FOUR = 12,
    CIRCLE_FIVE = 13,
    CIRCLE_SIX = 14,
    CIRCLE_SEVEN = 15,
    CIRCLE_EIGHT =16,
    CIRCLE_NINE = 17,
    WAN_ONE = 18,
    WAN_TWO = 19,
    WAN_THREE = 20,
    WAN_FOUR = 21,
    WAN_FIVE = 22,
    WAN_SIX = 23,
    WAN_SEVEN = 24,
    WAN_EIGHT = 25,
    WAN_NINE = 26,
    SPECIAL_RED_DRAGON = 27,
    SPECIAL_GREEN_DRAGON = 28,
    SPECIAL_WHITE_DRAGON = 29,
    SPECIAL_EAST = 30,
    SPECIAL_SOUTH = 31,
    SPECIAL_WEST = 32,
    SPECIAL_NORTH = 33,
    NONE = 100
};

class Player {
    
    vector<int> cnt;

public:
    vector<TILE_TYPE> tiles;
    Player(const vector<TILE_TYPE>& tiles);
    Player(Player* const);
    void add(const vector<TILE_TYPE>& tiles);
    void remove(const vector<TILE_TYPE>& tiles);

    bool can_complete(const TILE_TYPE& tile = TILE_TYPE::NONE);
    bool can_chow(const TILE_TYPE& tile, vector<vector<TILE_TYPE>>& sols);
    bool can_pung(const TILE_TYPE& tile);
};

