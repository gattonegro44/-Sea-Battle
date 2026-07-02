// seabattle.cpp
#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <algorithm>
#include <cctype>
#include <ctime>

using namespace std;

const string RESET = "\033[0m";
const string BLUE = "\033[94m";
const string GREEN = "\033[92m";
const string RED = "\033[91m";
const string YELLOW = "\033[93m";
const string CYAN = "\033[96m";
const string GRAY = "\033[90m";
const string BOLD = "\033[1m";

string colorize(const string& text, const string& color) {
    return color + text + RESET;
}

const int SIZE = 10;
vector<int> SHIP_LENGTHS = {4, 3, 3, 2, 2, 2, 1, 1, 1, 1};

class SeaBattle {
public:
    vector<vector<char>> board1, board2; // свои и врага
    vector<vector<char>> shot1, shot2;   // выстрелы
    vector<vector<pair<int,int>>> ships1, ships2;
    vector<pair<int,int>> alive1, alive2;
    int shots, hits;
    int turn;
    string mode, difficulty;
    bool manual;

    SeaBattle(string m, string d, bool man) : mode(m), difficulty(d), manual(man), shots(0), hits(0), turn(0) {
        board1.assign(SIZE, vector<char>(SIZE, '~'));
        board2.assign(SIZE, vector<char>(SIZE, '~'));
        shot1.assign(SIZE, vector<char>(SIZE, '~'));
        shot2.assign(SIZE, vector<char>(SIZE, '~'));
    }

    pair<int,int> parseCoord(const string& s) {
        if (s.size() < 2) return {-1,-1};
        char colChar = toupper(s[0]);
        if (colChar < 'A' || colChar > 'J') return {-1,-1};
        int col = colChar - 'A';
        int row = stoi(s.substr(1)) - 1;
        if (row < 0 || row >= SIZE || col < 0 || col >= SIZE) return {-1,-1};
        return {row, col};
    }

    string coordStr(int r, int c) {
        return string(1, char('A'+c)) + to_string(r+1);
    }

    bool canPlace(vector<vector<char>>& board, int row, int col, int length, char dir) {
        for (int i=0; i<length; ++i) {
            int r = row + (dir=='v' ? i : 0);
            int c = col + (dir=='h' ? i : 0);
            if (r>=SIZE || c>=SIZE || board[r][c] != '~') return false;
            for (int dr=-1; dr<=1; ++dr)
                for (int dc=-1; dc<=1; ++dc) {
                    int nr = r+dr, nc = c+dc;
                    if (nr>=0 && nr<SIZE && nc>=0 && nc<SIZE && board[nr][nc] != '~' && board[nr][nc] != '#') {
                        if (board[nr][nc] == 'S' || board[nr][nc] == 'X') return false;
                    }
                }
        }
        return true;
    }

    void placeShip(vector<vector<char>>& board, int row, int col, int length, char dir) {
        for (int i=0; i<length; ++i) {
            int r = row + (dir=='v' ? i : 0);
            int c = col + (dir=='h' ? i : 0);
            board[r][c] = 'S';
        }
    }

    void placeRandom(vector<vector<char>>& board, vector<vector<pair<int,int>>>& ships) {
        random_device rd;
        mt19937 gen(rd());
        uniform_int_distribution<> dis(0, SIZE-1);
        uniform_int_distribution<> dirDis(0,1);
        for (int length : SHIP_LENGTHS) {
            bool placed = false;
            int attempts = 0;
            while (!placed && attempts < 1000) {
                attempts++;
                int row = dis(gen), col = dis(gen);
                char dir = dirDis(gen) ? 'h' : 'v';
                if (canPlace(board, row, col, length, dir)) {
                    placeShip(board, row, col, length, dir);
                    vector<pair<int,int>> coords;
                    for (int i=0; i<length; ++i) {
                        int r = row + (dir=='v' ? i : 0);
                        int c = col + (dir=='h' ? i : 0);
                        coords.push_back({r,c});
                    }
                    ships.push_back(coords);
                    placed = true;
                }
            }
            if (!placed) {
                board.assign(SIZE, vector<char>(SIZE, '~'));
                ships.clear();
                placeRandom(board, ships);
                return;
            }
        }
    }

    void manualPlace(vector<vector<char>>& board, vector<vector<pair<int,int>>>& ships) {
        cout << "Ручная расстановка кораблей.\n";
        for (int length : SHIP_LENGTHS) {
            bool placed = false;
            while (!placed) {
                cout << "Разместите корабль длины " << length << "\n";
                printBoard(board, true);
                string coord, dir;
                cout << "Введите координату (A1): ";
                cin >> coord;
                if (coord == "q") exit(0);
                cout << "Введите направление (h/v): ";
                cin >> dir;
                auto p = parseCoord(coord);
                if (p.first == -1 || (dir!="h" && dir!="v")) {
                    cout << "Неверный ввод.\n";
                    continue;
                }
                int row = p.first, col = p.second;
                if (canPlace(board, row, col, length, dir[0])) {
                    placeShip(board, row, col, length, dir[0]);
                    vector<pair<int,int>> coords;
                    for (int i=0; i<length; ++i) {
                        int r = row + (dir[0]=='v' ? i : 0);
                        int c = col + (dir[0]=='h' ? i : 0);
                        coords.push_back({r,c});
                    }
                    ships.push_back(coords);
                    placed = true;
                } else {
                    cout << "Нельзя разместить здесь.\n";
                }
            }
        }
    }

    void printBoard(vector<vector<char>>& board, bool showShips = false) {
        cout << "   ";
        for (int i=0; i<SIZE; ++i) cout << char('A'+i) << " ";
        cout << "\n";
        for (int r=0; r<SIZE; ++r) {
            cout << (r+1) << " ";
            if (r+1 < 10) cout << " ";
            for (int c=0; c<SIZE; ++c) {
                char cell = board[r][c];
                if (cell == '~') cout << colorize("·", GRAY) << " ";
                else if (cell == 'S' && showShips) cout << colorize("S", GREEN) << " ";
                else if (cell == 'X') cout << colorize("X", RED) << " ";
                else if (cell == 'O') cout << colorize("O", YELLOW) << " ";
                else cout << cell << " ";
            }
            cout << "\n";
        }
    }

    char makeShot(int row, int col, vector<pair<int,int>>& alive, vector<vector<char>>& shotBoard, vector<vector<char>>& enemyBoard) {
        if (enemyBoard[row][col] == 'S') {
            alive.erase(remove(alive.begin(), alive.end(), make_pair(row,col)), alive.end());
            shotBoard[row][col] = 'X';
            enemyBoard[row][col] = 'X';
            return 'X';
        } else {
            shotBoard[row][col] = 'O';
            enemyBoard[row][col] = 'O';
            return 'O';
        }
    }

    void printDual() {
        cout << "\nВаше поле:\n";
        printBoard(board1, true);
        cout << "\nПоле противника:\n";
        printBoard(shot2, false);
        cout << "Выстрелов: " << shots << ", Попаданий: " << hits << "\n";
    }

    int playerTurn() {
        while (true) {
            printDual();
            string coord;
            cout << "Ваш ход (A1): ";
            cin >> coord;
            if (coord == "q") exit(0);
            auto p = parseCoord(coord);
            if (p.first == -1) {
                cout << "Неверный формат.\n";
                continue;
            }
            int row = p.first, col = p.second;
            if (shot2[row][col] != '~') {
                cout << "Сюда уже стреляли.\n";
                continue;
            }
            char res = makeShot(row, col, alive2, shot2, board2);
            shots++;
            if (res == 'X') {
                hits++;
                cout << "Попадание!\n";
                if (alive2.empty()) {
                    cout << "Все корабли противника потоплены! Вы победили!\n";
                    return 1; // win
                }
                continue;
            } else {
                cout << "Промах.\n";
                break;
            }
        }
        return 0;
    }

    int aiTurn() {
        random_device rd;
        mt19937 gen(rd());
        uniform_int_distribution<> dis(0, SIZE-1);
        while (true) {
            int row, col;
            if (difficulty == "easy") {
                row = dis(gen); col = dis(gen);
            } else {
                // Medium/Hard: ищем вокруг попаданий
                vector<pair<int,int>> candidates;
                for (int r=0; r<SIZE; ++r)
                    for (int c=0; c<SIZE; ++c)
                        if (shot1[r][c] == 'X') {
                            for (auto [dr, dc] : vector<pair<int,int>>{{1,0},{-1,0},{0,1},{0,-1}}) {
                                int nr=r+dr, nc=c+dc;
                                if (nr>=0 && nr<SIZE && nc>=0 && nc<SIZE && shot1[nr][nc] == '~')
                                    candidates.push_back({nr,nc});
                            }
                        }
                if (!candidates.empty()) {
                    auto p = candidates[dis(gen) % candidates.size()];
                    row = p.first; col = p.second;
                } else {
                    row = dis(gen); col = dis(gen);
                }
            }
            if (shot1[row][col] == '~') {
                char res = makeShot(row, col, alive1, shot1, board1);
                shots++;
                if (res == 'X') {
                    hits++;
                    cout << "Компьютер попал! (" << coordStr(row,col) << ")\n";
                    if (alive1.empty()) {
                        cout << "Все ваши корабли потоплены! Вы проиграли.\n";
                        return -1;
                    }
                    continue;
                } else {
                    cout << "Компьютер промахнулся. (" << coordStr(row,col) << ")\n";
                    break;
                }
            }
        }
        return 0;
    }

    void setup() {
        if (mode == "single") {
            if (manual) {
                manualPlace(board1, ships1);
            } else {
                placeRandom(board1, ships1);
            }
            placeRandom(board2, ships2);
            for (auto ship : ships1) for (auto p : ship) alive1.push_back(p);
            for (auto ship : ships2) for (auto p : ship) alive2.push_back(p);
        } else {
            cout << "Игрок 1, расставляйте корабли.\n";
            if (manual) manualPlace(board1, ships1);
            else placeRandom(board1, ships1);
            cout << "Игрок 2, расставляйте корабли.\n";
            if (manual) manualPlace(board2, ships2);
            else placeRandom(board2, ships2);
            for (auto ship : ships1) for (auto p : ship) alive1.push_back(p);
            for (auto ship : ships2) for (auto p : ship) alive2.push_back(p);
        }
    }

    void play() {
        setup();
        if (mode == "single") {
            while (true) {
                if (turn == 0) {
                    int res = playerTurn();
                    if (res == 1) break;
                    turn = 1;
                } else {
                    int res = aiTurn();
                    if (res == -1) break;
                    turn = 0;
                }
            }
        } else {
            cout << "Режим двух игроков пока не реализован.\n";
        }
    }
};

int main(int argc, char* argv[]) {
    string mode = "single", difficulty = "easy";
    bool manual = false;
    if (argc > 1) {
        if (string(argv[1]) == "two") mode = "two";
        else if (string(argv[1]) == "single") mode = "single";
    }
    for (int i=2; i<argc; ++i) {
        string arg = argv[i];
        if (arg == "-d" || arg == "--difficulty") {
            if (i+1 < argc) {
                difficulty = argv[++i];
            }
        } else if (arg == "-p" || arg == "--place") {
            manual = true;
        }
    }
    SeaBattle game(mode, difficulty, manual);
    game.play();
    return 0;
}
