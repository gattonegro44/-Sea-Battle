// seabattle.java
import java.io.*;
import java.util.*;

public class seabattle {
    private static final String RESET = "\u001B[0m";
    private static final String BLUE = "\u001B[94m";
    private static final String GREEN = "\u001B[92m";
    private static final String RED = "\u001B[91m";
    private static final String YELLOW = "\u001B[93m";
    private static final String GRAY = "\u001B[90m";

    private static String colorize(String text, String color) {
        return color + text + RESET;
    }

    private static final int SIZE = 10;
    private static final int[] SHIP_LENGTHS = {4,3,3,2,2,2,1,1,1,1};

    private char[][] board1 = new char[SIZE][SIZE];
    private char[][] board2 = new char[SIZE][SIZE];
    private char[][] shot1 = new char[SIZE][SIZE];
    private char[][] shot2 = new char[SIZE][SIZE];
    private List<List<int[]>> ships1 = new ArrayList<>();
    private List<List<int[]>> ships2 = new ArrayList<>();
    private Set<String> alive1 = new HashSet<>();
    private Set<String> alive2 = new HashSet<>();
    private int shots = 0, hits = 0, turn = 0;
    private String mode, difficulty;
    private boolean manual;
    private BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));

    public seabattle(String mode, String difficulty, boolean manual) {
        this.mode = mode;
        this.difficulty = difficulty;
        this.manual = manual;
        for (int i=0; i<SIZE; i++) {
            Arrays.fill(board1[i], '~');
            Arrays.fill(board2[i], '~');
            Arrays.fill(shot1[i], '~');
            Arrays.fill(shot2[i], '~');
        }
    }

    private int[] parseCoord(String s) {
        if (s.length() < 2) return null;
        char colChar = Character.toUpperCase(s.charAt(0));
        if (colChar < 'A' || colChar > 'J') return null;
        int col = colChar - 'A';
        int row;
        try { row = Integer.parseInt(s.substring(1)) - 1; }
        catch (NumberFormatException e) { return null; }
        if (row < 0 || row >= SIZE || col < 0 || col >= SIZE) return null;
        return new int[]{row, col};
    }

    private String coordStr(int r, int c) {
        return "" + (char)('A'+c) + (r+1);
    }

    private boolean canPlace(char[][] board, int row, int col, int length, char dir) {
        for (int i=0; i<length; i++) {
            int r = dir=='v' ? row+i : row;
            int c = dir=='h' ? col+i : col;
            if (r>=SIZE || c>=SIZE || board[r][c] != '~') return false;
            for (int dr=-1; dr<=1; dr++)
                for (int dc=-1; dc<=1; dc++) {
                    int nr=r+dr, nc=c+dc;
                    if (nr>=0 && nr<SIZE && nc>=0 && nc<SIZE && board[nr][nc] != '~' && board[nr][nc] != '#') {
                        if (board[nr][nc] == 'S' || board[nr][nc] == 'X') return false;
                    }
                }
        }
        return true;
    }

    private void placeShip(char[][] board, int row, int col, int length, char dir) {
        for (int i=0; i<length; i++) {
            int r = dir=='v' ? row+i : row;
            int c = dir=='h' ? col+i : col;
            board[r][c] = 'S';
        }
    }

    private void placeRandom(char[][] board, List<List<int[]>> ships) {
        Random rand = new Random();
        for (int length : SHIP_LENGTHS) {
            boolean placed = false;
            int attempts = 0;
            while (!placed && attempts < 1000) {
                attempts++;
                int row = rand.nextInt(SIZE), col = rand.nextInt(SIZE);
                char dir = rand.nextBoolean() ? 'h' : 'v';
                if (canPlace(board, row, col, length, dir)) {
                    placeShip(board, row, col, length, dir);
                    List<int[]> coords = new ArrayList<>();
                    for (int i=0; i<length; i++) {
                        int r = dir=='v' ? row+i : row;
                        int c = dir=='h' ? col+i : col;
                        coords.add(new int[]{r,c});
                    }
                    ships.add(coords);
                    placed = true;
                }
            }
            if (!placed) {
                for (int i=0; i<SIZE; i++) Arrays.fill(board[i], '~');
                ships.clear();
                placeRandom(board, ships);
                return;
            }
        }
    }

    private void manualPlace(char[][] board, List<List<int[]>> ships) throws IOException {
        System.out.println("Ручная расстановка кораблей.");
        for (int length : SHIP_LENGTHS) {
            boolean placed = false;
            while (!placed) {
                System.out.println("Разместите корабль длины " + length);
                printBoard(board, true);
                System.out.print("Введите координату (A1): ");
                String coord = reader.readLine().trim();
                if (coord.equals("q")) System.exit(0);
                System.out.print("Введите направление (h/v): ");
                String dir = reader.readLine().trim();
                int[] pos = parseCoord(coord);
                if (pos == null || (!dir.equals("h") && !dir.equals("v"))) {
                    System.out.println("Неверный ввод.");
                    continue;
                }
                int row = pos[0], col = pos[1];
                if (canPlace(board, row, col, length, dir.charAt(0))) {
                    placeShip(board, row, col, length, dir.charAt(0));
                    List<int[]> coords = new ArrayList<>();
                    for (int i=0; i<length; i++) {
                        int r = dir.charAt(0)=='v' ? row+i : row;
                        int c = dir.charAt(0)=='h' ? col+i : col;
                        coords.add(new int[]{r,c});
                    }
                    ships.add(coords);
                    placed = true;
                } else {
                    System.out.println("Нельзя разместить здесь.");
                }
            }
        }
    }

    private void printBoard(char[][] board, boolean showShips) {
        System.out.print("   ");
        for (int i=0; i<SIZE; i++) System.out.print((char)('A'+i) + " ");
        System.out.println();
        for (int r=0; r<SIZE; r++) {
            System.out.printf("%2d ", r+1);
            for (int c=0; c<SIZE; c++) {
                char cell = board[r][c];
                if (cell == '~') System.out.print(colorize("· ", GRAY));
                else if (cell == 'S' && showShips) System.out.print(colorize("S ", GREEN));
                else if (cell == 'X') System.out.print(colorize("X ", RED));
                else if (cell == 'O') System.out.print(colorize("O ", YELLOW));
                else System.out.print(cell + " ");
            }
            System.out.println();
        }
    }

    private char makeShot(int row, int col, Set<String> alive, char[][] shotBoard, char[][] enemyBoard) {
        if (enemyBoard[row][col] == 'S') {
            alive.remove(row+","+col);
            shotBoard[row][col] = 'X';
            enemyBoard[row][col] = 'X';
            return 'X';
        } else {
            shotBoard[row][col] = 'O';
            enemyBoard[row][col] = 'O';
            return 'O';
        }
    }

    private void printDual() {
        System.out.println("\nВаше поле:");
        printBoard(board1, true);
        System.out.println("\nПоле противника:");
        printBoard(shot2, false);
        System.out.printf("Выстрелов: %d, Попаданий: %d\n", shots, hits);
    }

    private int playerTurn() throws IOException {
        while (true) {
            printDual();
            System.out.print("Ваш ход (A1): ");
            String coord = reader.readLine().trim();
            if (coord.equals("q")) System.exit(0);
            int[] pos = parseCoord(coord);
            if (pos == null) {
                System.out.println("Неверный формат.");
                continue;
            }
            int row = pos[0], col = pos[1];
            if (shot2[row][col] != '~') {
                System.out.println("Сюда уже стреляли.");
                continue;
            }
            char res = makeShot(row, col, alive2, shot2, board2);
            shots++;
            if (res == 'X') {
                hits++;
                System.out.println("Попадание!");
                if (alive2.isEmpty()) {
                    System.out.println("Все корабли противника потоплены! Вы победили!");
                    return 1;
                }
                continue;
            } else {
                System.out.println("Промах.");
                break;
            }
        }
        return 0;
    }

    private int aiTurn() {
        Random rand = new Random();
        while (true) {
            int row, col;
            if (difficulty.equals("easy")) {
                row = rand.nextInt(SIZE);
                col = rand.nextInt(SIZE);
            } else {
                List<int[]> candidates = new ArrayList<>();
                for (int r=0; r<SIZE; r++)
                    for (int c=0; c<SIZE; c++)
                        if (shot1[r][c] == 'X') {
                            int[][] dirs = {{1,0},{-1,0},{0,1},{0,-1}};
                            for (int[] d : dirs) {
                                int nr=r+d[0], nc=c+d[1];
                                if (nr>=0 && nr<SIZE && nc>=0 && nc<SIZE && shot1[nr][nc] == '~')
                                    candidates.add(new int[]{nr,nc});
                            }
                        }
                if (!candidates.isEmpty()) {
                    int[] p = candidates.get(rand.nextInt(candidates.size()));
                    row = p[0]; col = p[1];
                } else {
                    row = rand.nextInt(SIZE);
                    col = rand.nextInt(SIZE);
                }
            }
            if (shot1[row][col] == '~') {
                char res = makeShot(row, col, alive1, shot1, board1);
                shots++;
                if (res == 'X') {
                    hits++;
                    System.out.println("Компьютер попал! (" + coordStr(row,col) + ")");
                    if (alive1.isEmpty()) {
                        System.out.println("Все ваши корабли потоплены! Вы проиграли.");
                        return -1;
                    }
                    continue;
                } else {
                    System.out.println("Компьютер промахнулся. (" + coordStr(row,col) + ")");
                    break;
                }
            }
        }
        return 0;
    }

    private void setup() throws IOException {
        if (mode.equals("single")) {
            if (manual) manualPlace(board1, ships1);
            else placeRandom(board1, ships1);
            placeRandom(board2, ships2);
            for (List<int[]> ship : ships1) for (int[] p : ship) alive1.add(p[0]+","+p[1]);
            for (List<int[]> ship : ships2) for (int[] p : ship) alive2.add(p[0]+","+p[1]);
        } else {
            System.out.println("Режим двух игроков пока не реализован.");
        }
    }

    public void play() throws IOException {
        setup();
        if (mode.equals("single")) {
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
        }
    }

    public static void main(String[] args) throws IOException {
        String mode = "single", difficulty = "easy";
        boolean manual = false;
        if (args.length > 0 && args[0].equals("two")) mode = "two";
        for (int i=1; i<args.length; i++) {
            if (args[i].equals("-d") || args[i].equals("--difficulty")) {
                if (i+1 < args.length) difficulty = args[++i];
            } else if (args[i].equals("-p") || args[i].equals("--place")) {
                manual = true;
            }
        }
        seabattle game = new seabattle(mode, difficulty, manual);
        game.play();
    }
}
