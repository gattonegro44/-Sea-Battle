// seabattle.go
package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"strings"
	"time"
)

const SIZE = 10

var colors = map[string]string{
	"reset": "\033[0m",
	"blue": "\033[94m",
	"green": "\033[92m",
	"red": "\033[91m",
	"yellow": "\033[93m",
	"cyan": "\033[96m",
	"gray": "\033[90m",
	"bold": "\033[1m",
}

func colorize(text, color string) string {
	return colors[color] + text + colors["reset"]
}

var SHIP_LENGTHS = []int{4,3,3,2,2,2,1,1,1,1}

type SeaBattle struct {
	board1, board2 [][]byte
	shot1, shot2   [][]byte
	ships1, ships2 [][][2]int
	alive1, alive2 [][2]int
	shots, hits    int
	turn           int
	mode, difficulty string
	manual         bool
	reader         *bufio.Reader
}

func NewSeaBattle(mode, difficulty string, manual bool) *SeaBattle {
	b := &SeaBattle{
		mode: mode,
		difficulty: difficulty,
		manual: manual,
		reader: bufio.NewReader(os.Stdin),
	}
	b.board1 = make([][]byte, SIZE)
	b.board2 = make([][]byte, SIZE)
	b.shot1 = make([][]byte, SIZE)
	b.shot2 = make([][]byte, SIZE)
	for i := 0; i < SIZE; i++ {
		b.board1[i] = make([]byte, SIZE)
		b.board2[i] = make([]byte, SIZE)
		b.shot1[i] = make([]byte, SIZE)
		b.shot2[i] = make([]byte, SIZE)
		for j := 0; j < SIZE; j++ {
			b.board1[i][j] = '~'
			b.board2[i][j] = '~'
			b.shot1[i][j] = '~'
			b.shot2[i][j] = '~'
		}
	}
	return b
}

func (b *SeaBattle) parseCoord(s string) (int, int) {
	if len(s) < 2 { return -1, -1 }
	colChar := s[0]
	if colChar >= 'a' && colChar <= 'z' { colChar -= 32 }
	if colChar < 'A' || colChar > 'J' { return -1, -1 }
	col := int(colChar - 'A')
	row, err := strconv.Atoi(s[1:])
	if err != nil || row < 1 || row > SIZE { return -1, -1 }
	return row-1, col
}

func (b *SeaBattle) coordStr(r, c int) string {
	return string(rune('A'+c)) + strconv.Itoa(r+1)
}

func (b *SeaBattle) canPlace(board [][]byte, row, col, length int, dir byte) bool {
	for i := 0; i < length; i++ {
		var r, c int
		if dir == 'v' {
			r, c = row+i, col
		} else {
			r, c = row, col+i
		}
		if r >= SIZE || c >= SIZE || board[r][c] != '~' { return false }
		for dr := -1; dr <= 1; dr++ {
			for dc := -1; dc <= 1; dc++ {
				nr, nc := r+dr, c+dc
				if nr >= 0 && nr < SIZE && nc >= 0 && nc < SIZE && board[nr][nc] != '~' && board[nr][nc] != '#' {
					if board[nr][nc] == 'S' || board[nr][nc] == 'X' { return false }
				}
			}
		}
	}
	return true
}

func (b *SeaBattle) placeShip(board [][]byte, row, col, length int, dir byte) {
	for i := 0; i < length; i++ {
		var r, c int
		if dir == 'v' {
			r, c = row+i, col
		} else {
			r, c = row, col+i
		}
		board[r][c] = 'S'
	}
}

func (b *SeaBattle) placeRandom(board [][]byte, ships *[][][2]int) {
	rand.Seed(time.Now().UnixNano())
	for _, length := range SHIP_LENGTHS {
		placed := false
		attempts := 0
		for !placed && attempts < 1000 {
			attempts++
			row, col := rand.Intn(SIZE), rand.Intn(SIZE)
			dir := 'h'
			if rand.Intn(2) == 0 { dir = 'v' }
			if b.canPlace(board, row, col, length, byte(dir)) {
				b.placeShip(board, row, col, length, byte(dir))
				var coords [][2]int
				for i := 0; i < length; i++ {
					var r, c int
					if dir == 'v' {
						r, c = row+i, col
					} else {
						r, c = row, col+i
					}
					coords = append(coords, [2]int{r, c})
				}
				*ships = append(*ships, coords)
				placed = true
			}
		}
		if !placed {
			// reset and retry
			for i := range board {
				for j := range board[i] {
					board[i][j] = '~'
				}
			}
			*ships = [][][2]int{}
			b.placeRandom(board, ships)
			return
		}
	}
}

func (b *SeaBattle) manualPlace(board [][]byte, ships *[][][2]int) {
	fmt.Println("Ручная расстановка кораблей.")
	for _, length := range SHIP_LENGTHS {
		placed := false
		for !placed {
			fmt.Printf("Разместите корабль длины %d\n", length)
			b.printBoard(board, true)
			fmt.Print("Введите координату (A1): ")
			coord, _ := b.reader.ReadString('\n')
			coord = strings.TrimSpace(coord)
			if coord == "q" { os.Exit(0) }
			fmt.Print("Введите направление (h/v): ")
			dir, _ := b.reader.ReadString('\n')
			dir = strings.TrimSpace(dir)
			if len(dir) != 1 || (dir != "h" && dir != "v") {
				fmt.Println("Неверный ввод.")
				continue
			}
			row, col := b.parseCoord(coord)
			if row == -1 {
				fmt.Println("Неверные координаты.")
				continue
			}
			if b.canPlace(board, row, col, length, dir[0]) {
				b.placeShip(board, row, col, length, dir[0])
				var coords [][2]int
				for i := 0; i < length; i++ {
					var r, c int
					if dir[0] == 'v' {
						r, c = row+i, col
					} else {
						r, c = row, col+i
					}
					coords = append(coords, [2]int{r, c})
				}
				*ships = append(*ships, coords)
				placed = true
			} else {
				fmt.Println("Нельзя разместить здесь.")
			}
		}
	}
}

func (b *SeaBattle) printBoard(board [][]byte, showShips bool) {
	fmt.Print("   ")
	for i := 0; i < SIZE; i++ {
		fmt.Printf("%c ", 'A'+i)
	}
	fmt.Println()
	for r := 0; r < SIZE; r++ {
		fmt.Printf("%2d ", r+1)
		for c := 0; c < SIZE; c++ {
			cell := board[r][c]
			if cell == '~' {
				fmt.Print(colorize("· ", "gray"))
			} else if cell == 'S' && showShips {
				fmt.Print(colorize("S ", "green"))
			} else if cell == 'X' {
				fmt.Print(colorize("X ", "red"))
			} else if cell == 'O' {
				fmt.Print(colorize("O ", "yellow"))
			} else {
				fmt.Printf("%c ", cell)
			}
		}
		fmt.Println()
	}
}

func (b *SeaBattle) makeShot(row, col int, alive *[][2]int, shotBoard, enemyBoard [][]byte) byte {
	if enemyBoard[row][col] == 'S' {
		// удалить из alive
		newAlive := [][2]int{}
		for _, p := range *alive {
			if !(p[0] == row && p[1] == col) {
				newAlive = append(newAlive, p)
			}
		}
		*alive = newAlive
		shotBoard[row][col] = 'X'
		enemyBoard[row][col] = 'X'
		return 'X'
	} else {
		shotBoard[row][col] = 'O'
		enemyBoard[row][col] = 'O'
		return 'O'
	}
}

func (b *SeaBattle) printDual() {
	fmt.Println("\nВаше поле:")
	b.printBoard(b.board1, true)
	fmt.Println("\nПоле противника:")
	b.printBoard(b.shot2, false)
	fmt.Printf("Выстрелов: %d, Попаданий: %d\n", b.shots, b.hits)
}

func (b *SeaBattle) playerTurn() int {
	for {
		b.printDual()
		fmt.Print("Ваш ход (A1): ")
		coord, _ := b.reader.ReadString('\n')
		coord = strings.TrimSpace(coord)
		if coord == "q" { os.Exit(0) }
		row, col := b.parseCoord(coord)
		if row == -1 {
			fmt.Println("Неверный формат.")
			continue
		}
		if b.shot2[row][col] != '~' {
			fmt.Println("Сюда уже стреляли.")
			continue
		}
		res := b.makeShot(row, col, &b.alive2, b.shot2, b.board2)
		b.shots++
		if res == 'X' {
			b.hits++
			fmt.Println("Попадание!")
			if len(b.alive2) == 0 {
				fmt.Println("Все корабли противника потоплены! Вы победили!")
				return 1
			}
			continue
		} else {
			fmt.Println("Промах.")
			break
		}
	}
	return 0
}

func (b *SeaBattle) aiTurn() int {
	rand.Seed(time.Now().UnixNano())
	for {
		var row, col int
		if b.difficulty == "easy" {
			row, col = rand.Intn(SIZE), rand.Intn(SIZE)
		} else {
			var candidates [][2]int
			for r := 0; r < SIZE; r++ {
				for c := 0; c < SIZE; c++ {
					if b.shot1[r][c] == 'X' {
						for _, d := range [][2]int{{1,0},{-1,0},{0,1},{0,-1}} {
							nr, nc := r+d[0], c+d[1]
							if nr >= 0 && nr < SIZE && nc >= 0 && nc < SIZE && b.shot1[nr][nc] == '~' {
								candidates = append(candidates, [2]int{nr, nc})
							}
						}
					}
				}
			}
			if len(candidates) > 0 {
				idx := rand.Intn(len(candidates))
				row, col = candidates[idx][0], candidates[idx][1]
			} else {
				row, col = rand.Intn(SIZE), rand.Intn(SIZE)
			}
		}
		if b.shot1[row][col] == '~' {
			res := b.makeShot(row, col, &b.alive1, b.shot1, b.board1)
			b.shots++
			if res == 'X' {
				b.hits++
				fmt.Printf("Компьютер попал! (%s)\n", b.coordStr(row, col))
				if len(b.alive1) == 0 {
					fmt.Println("Все ваши корабли потоплены! Вы проиграли.")
					return -1
				}
				continue
			} else {
				fmt.Printf("Компьютер промахнулся. (%s)\n", b.coordStr(row, col))
				break
			}
		}
	}
	return 0
}

func (b *SeaBattle) setup() {
	if b.mode == "single" {
		if b.manual {
			b.manualPlace(b.board1, &b.ships1)
		} else {
			b.placeRandom(b.board1, &b.ships1)
		}
		b.placeRandom(b.board2, &b.ships2)
		for _, ship := range b.ships1 {
			for _, p := range ship {
				b.alive1 = append(b.alive1, p)
			}
		}
		for _, ship := range b.ships2 {
			for _, p := range ship {
				b.alive2 = append(b.alive2, p)
			}
		}
	} else {
		fmt.Println("Режим двух игроков пока не реализован.")
	}
}

func (b *SeaBattle) play() {
	b.setup()
	if b.mode == "single" {
		for {
			if b.turn == 0 {
				res := b.playerTurn()
				if res == 1 { break }
				b.turn = 1
			} else {
				res := b.aiTurn()
				if res == -1 { break }
				b.turn = 0
			}
		}
	}
}

func main() {
	mode := "single"
	difficulty := "easy"
	manual := false
	if len(os.Args) > 1 {
		if os.Args[1] == "two" { mode = "two" }
	}
	for i := 2; i < len(os.Args); i++ {
		if os.Args[i] == "-d" || os.Args[i] == "--difficulty" {
			if i+1 < len(os.Args) {
				difficulty = os.Args[i+1]
				i++
			}
		} else if os.Args[i] == "-p" || os.Args[i] == "--place" {
			manual = true
		}
	}
	game := NewSeaBattle(mode, difficulty, manual)
	game.play()
}
