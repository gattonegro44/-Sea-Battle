// seabattle.cs
using System;
using System.Collections.Generic;
using System.Linq;

class SeaBattle
{
    static string Colorize(string text, string color)
    {
        string col = color switch
        {
            "blue" => "\x1b[94m",
            "green" => "\x1b[92m",
            "red" => "\x1b[91m",
            "yellow" => "\x1b[93m",
            "gray" => "\x1b[90m",
            _ => "\x1b[0m"
        };
        return col + text + "\x1b[0m";
    }

    const int SIZE = 10;
    static int[] SHIP_LENGTHS = {4,3,3,2,2,2,1,1,1,1};

    char[,] board1 = new char[SIZE,SIZE];
    char[,] board2 = new char[SIZE,SIZE];
    char[,] shot1 = new char[SIZE,SIZE];
    char[,] shot2 = new char[SIZE,SIZE];
    List<List<(int,int)>> ships1 = new List<List<(int,int)>>();
    List<List<(int,int)>> ships2 = new List<List<(int,int)>>();
    List<(int,int)> alive1 = new List<(int,int)>();
    List<(int,int)> alive2 = new List<(int,int)>();
    int shots = 0, hits = 0;
    int turn = 0;
    string mode, difficulty;
    bool manual;

    public SeaBattle(string mode, string difficulty, bool manual)
    {
        this.mode = mode;
        this.difficulty = difficulty;
        this.manual = manual;
        for (int i=0; i<SIZE; i++) for (int j=0; j<SIZE; j++) {
            board1[i,j] = '~'; board2[i,j] = '~';
            shot1[i,j] = '~'; shot2[i,j] = '~';
        }
    }

    (int,int) ParseCoord(string s)
    {
        if (s.Length < 2) return (-1,-1);
        char colChar = char.ToUpper(s[0]);
        if (colChar < 'A' || colChar > 'J') return (-1,-1);
        int col = colChar - 'A';
        if (!int.TryParse(s.Substring(1), out int row)) return (-1,-1);
        row--;
        if (row < 0 || row >= SIZE || col < 0 || col >= SIZE) return (-1,-1);
        return (row, col);
    }

    string CoordStr(int r, int c) => $"{(char)('A'+c)}{r+1}";

    bool CanPlace(char[,] board, int row, int col, int length, char dir)
    {
        for (int i=0; i<length; i++)
        {
            int r = dir=='v' ? row+i : row;
            int c = dir=='h' ? col+i : col;
            if (r>=SIZE || c>=SIZE || board[r,c] != '~') return false;
            for (int dr=-1; dr<=1; dr++)
                for (int dc=-1; dc<=1; dc++)
                {
                    int nr=r+dr, nc=c+dc;
                    if (nr>=0 && nr<SIZE && nc>=0 && nc<SIZE && board[nr,nc] != '~' && board[nr,nc] != '#')
                        if (board[nr,nc] == 'S' || board[nr,nc] == 'X') return false;
                }
        }
        return true;
    }

    void PlaceShip(char[,] board, int row, int col, int length, char dir)
    {
        for (int i=0; i<length; i++)
        {
            int r = dir=='v' ? row+i : row;
            int c = dir=='h' ? col+i : col;
            board[r,c] = 'S';
        }
    }

    void PlaceRandom(char[,] board, List<List<(int,int)>> ships)
    {
        Random rand = new Random();
        foreach (int length in SHIP_LENGTHS)
        {
            bool placed = false;
            int attempts = 0;
            while (!placed && attempts < 1000)
            {
                attempts++;
                int row = rand.Next(SIZE), col = rand.Next(SIZE);
                char dir = rand.Next(2)==0 ? 'h' : 'v';
                if (CanPlace(board, row, col, length, dir))
                {
                    PlaceShip(board, row, col, length, dir);
                    var coords = new List<(int,int)>();
                    for (int i=0; i<length; i++)
                    {
                        int r = dir=='v' ? row+i : row;
                        int c = dir=='h' ? col+i : col;
                        coords.Add((r,c));
                    }
                    ships.Add(coords);
                    placed = true;
                }
            }
            if (!placed)
            {
                for (int i=0; i<SIZE; i++) for (int j=0; j<SIZE; j++) board[i,j] = '~';
                ships.Clear();
                PlaceRandom(board, ships);
                return;
            }
        }
    }

    void ManualPlace(char[,] board, List<List<(int,int)>> ships)
    {
        Console.WriteLine("Ручная расстановка кораблей.");
        foreach (int length in SHIP_LENGTHS)
        {
            bool placed = false;
            while (!placed)
            {
                Console.WriteLine($"Разместите корабль длины {length}");
                PrintBoard(board, true);
                Console.Write("Введите координату (A1): ");
                string coord = Console.ReadLine().Trim();
                if (coord == "q") Environment.Exit(0);
                Console.Write("Введите направление (h/v): ");
                string dir = Console.ReadLine().Trim();
                var p = ParseCoord(coord);
                if (p.Item1 == -1 || (dir!="h" && dir!="v")) { Console.WriteLine("Неверный ввод."); continue; }
                int row = p.Item1, col = p.Item2;
                if (CanPlace(board, row, col, length, dir[0]))
                {
                    PlaceShip(board, row, col, length, dir[0]);
                    var coords = new List<(int,int)>();
                    for (int i=0; i<length; i++)
                    {
                        int r = dir[0]=='v' ? row+i : row;
                        int c = dir[0]=='h' ? col+i : col;
                        coords.Add((r,c));
                    }
                    ships.Add(coords);
                    placed = true;
                }
                else Console.WriteLine("Нельзя разместить здесь.");
            }
        }
    }

    void PrintBoard(char[,] board, bool showShips=false)
    {
        Console.Write("   ");
        for (int i=0; i<SIZE; i++) Console.Write($"{(char)('A'+i)} ");
        Console.WriteLine();
        for (int r=0; r<SIZE; r++)
        {
            Console.Write($"{r+1,2} ");
            for (int c=0; c<SIZE; c++)
            {
                char cell = board[r,c];
                if (cell == '~') Console.Write(Colorize("· ", "gray"));
                else if (cell == 'S' && showShips) Console.Write(Colorize("S ", "green"));
                else if (cell == 'X') Console.Write(Colorize("X ", "red"));
                else if (cell == 'O') Console.Write(Colorize("O ", "yellow"));
                else Console.Write(cell + " ");
            }
            Console.WriteLine();
        }
    }

    char MakeShot(int row, int col, List<(int,int)> alive, char[,] shotBoard, char[,] enemyBoard)
    {
        if (enemyBoard[row,col] == 'S')
        {
            alive.Remove((row,col));
            shotBoard[row,col] = 'X';
            enemyBoard[row,col] = 'X';
            return 'X';
        }
        else
        {
            shotBoard[row,col] = 'O';
            enemyBoard[row,col] = 'O';
            return 'O';
        }
    }

    void PrintDual()
    {
        Console.WriteLine("\nВаше поле:");
        PrintBoard(board1, true);
        Console.WriteLine("\nПоле противника:");
        PrintBoard(shot2, false);
        Console.WriteLine($"Выстрелов: {shots}, Попаданий: {hits}");
    }

    int PlayerTurn()
    {
        while (true)
        {
            PrintDual();
            Console.Write("Ваш ход (A1): ");
            string coord = Console.ReadLine().Trim();
            if (coord == "q") Environment.Exit(0);
            var p = ParseCoord(coord);
            if (p.Item1 == -1) { Console.WriteLine("Неверный формат."); continue; }
            int row = p.Item1, col = p.Item2;
            if (shot2[row,col] != '~') { Console.WriteLine("Сюда уже стреляли."); continue; }
            char res = MakeShot(row, col, alive2, shot2, board2);
            shots++;
            if (res == 'X')
            {
                hits++;
                Console.WriteLine("Попадание!");
                if (alive2.Count == 0) { Console.WriteLine("Все корабли противника потоплены! Вы победили!"); return 1; }
                continue;
            }
            else
            {
                Console.WriteLine("Промах.");
                break;
            }
        }
        return 0;
    }

    int AiTurn()
    {
        Random rand = new Random();
        while (true)
        {
            int row, col;
            if (difficulty == "easy")
            {
                row = rand.Next(SIZE);
                col = rand.Next(SIZE);
            }
            else
            {
                var candidates = new List<(int,int)>();
                for (int r=0; r<SIZE; r++)
                    for (int c=0; c<SIZE; c++)
                        if (shot1[r,c] == 'X')
                        {
                            foreach (var (dr,dc) in new (int,int)[]{(1,0),(-1,0),(0,1),(0,-1)})
                            {
                                int nr=r+dr, nc=c+dc;
                                if (nr>=0 && nr<SIZE && nc>=0 && nc<SIZE && shot1[nr,nc] == '~')
                                    candidates.Add((nr,nc));
                            }
                        }
                if (candidates.Count > 0)
                {
                    var p = candidates[rand.Next(candidates.Count)];
                    row = p.Item1; col = p.Item2;
                }
                else
                {
                    row = rand.Next(SIZE);
                    col = rand.Next(SIZE);
                }
            }
            if (shot1[row,col] == '~')
            {
                char res = MakeShot(row, col, alive1, shot1, board1);
                shots++;
                if (res == 'X')
                {
                    hits++;
                    Console.WriteLine($"Компьютер попал! ({CoordStr(row,col)})");
                    if (alive1.Count == 0) { Console.WriteLine("Все ваши корабли потоплены! Вы проиграли."); return -1; }
                    continue;
                }
                else
                {
                    Console.WriteLine($"Компьютер промахнулся. ({CoordStr(row,col)})");
                    break;
                }
            }
        }
        return 0;
    }

    void Setup()
    {
        if (mode == "single")
        {
            if (manual) ManualPlace(board1, ships1);
            else PlaceRandom(board1, ships1);
            PlaceRandom(board2, ships2);
            alive1 = ships1.SelectMany(s => s).ToList();
            alive2 = ships2.SelectMany(s => s).ToList();
        }
        else
        {
            Console.WriteLine("Режим двух игроков пока не реализован.");
        }
    }

    public void Play()
    {
        Setup();
        if (mode == "single")
        {
            while (true)
            {
                if (turn == 0)
                {
                    int res = PlayerTurn();
                    if (res == 1) break;
                    turn = 1;
                }
                else
                {
                    int res = AiTurn();
                    if (res == -1) break;
                    turn = 0;
                }
            }
        }
    }

    static void Main(string[] args)
    {
        string mode = "single", difficulty = "easy";
        bool manual = false;
        if (args.Length > 0 && args[0] == "two") mode = "two";
        for (int i=1; i<args.Length; i++)
        {
            if (args[i] == "-d" || args[i] == "--difficulty")
            {
                if (i+1 < args.Length) difficulty = args[++i];
            }
            else if (args[i] == "-p" || args[i] == "--place")
                manual = true;
        }
        var game = new SeaBattle(mode, difficulty, manual);
        game.Play();
    }
}
