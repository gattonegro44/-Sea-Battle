# seabattle.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import random
import re
import copy
import time
import json
from pathlib import Path

# ANSI цвета
COLORS = {
    'reset': '\033[0m',
    'blue': '\033[94m',
    'green': '\033[92m',
    'red': '\033[91m',
    'yellow': '\033[93m',
    'cyan': '\033[96m',
    'gray': '\033[90m',
    'bold': '\033[1m'
}

def colorize(text, color):
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"

class SeaBattle:
    SIZE = 10
    SHIPS = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]  # длины кораблей
    SHIP_NAMES = {4: '4-палубный', 3: '3-палубный', 2: '2-палубный', 1: '1-палубный'}

    def __init__(self, mode='single', difficulty='easy', manual=False):
        self.mode = mode
        self.difficulty = difficulty
        self.manual = manual
        self.board1 = [['~']*self.SIZE for _ in range(self.SIZE)]  # свой флот
        self.board2 = [['~']*self.SIZE for _ in range(self.SIZE)]  # флот противника (невидимый)
        self.shot1 = [['~']*self.SIZE for _ in range(self.SIZE)]   # выстрелы по своему полю (для отображения)
        self.shot2 = [['~']*self.SIZE for _ in range(self.SIZE)]   # выстрелы по полю противника (для отображения)
        self.ships1 = []  # координаты кораблей игрока
        self.ships2 = []  # координаты кораблей противника
        self.alive1 = []  # живые клетки кораблей игрока
        self.alive2 = []  # живые клетки кораблей противника
        self.turn = 0  # 0 - игрок, 1 - компьютер
        self.shots = 0
        self.hits = 0
        self.sunk = 0

    def parse_coord(self, coord):
        """Преобразует координату типа 'A1' в (row, col)"""
        m = re.match(r'([A-Ja-j])(\d{1,2})$', coord)
        if not m:
            return None
        col = ord(m.group(1).upper()) - ord('A')
        row = int(m.group(2)) - 1
        if 0 <= row < self.SIZE and 0 <= col < self.SIZE:
            return (row, col)
        return None

    def coord_to_str(self, row, col):
        return f"{chr(ord('A')+col)}{row+1}"

    def place_ships_random(self, board, ships_list):
        """Случайное размещение кораблей на доске"""
        ships = []
        for length in self.SHIPS:
            placed = False
            attempts = 0
            while not placed and attempts < 1000:
                attempts += 1
                row = random.randint(0, self.SIZE-1)
                col = random.randint(0, self.SIZE-1)
                direction = random.choice(['h', 'v'])
                if self.can_place(board, row, col, length, direction):
                    self.place_ship(board, row, col, length, direction)
                    coords = []
                    for i in range(length):
                        if direction == 'h':
                            coords.append((row, col+i))
                        else:
                            coords.append((row+i, col))
                    ships.append(coords)
                    placed = True
            if not placed:
                # Если не удалось разместить, очищаем и пробуем заново
                board = [['~']*self.SIZE for _ in range(self.SIZE)]
                return self.place_ships_random(board, ships_list)
        return ships, board

    def can_place(self, board, row, col, length, direction):
        """Проверяет, можно ли разместить корабль"""
        for i in range(length):
            r = row + (i if direction == 'v' else 0)
            c = col + (i if direction == 'h' else 0)
            if r >= self.SIZE or c >= self.SIZE:
                return False
            if board[r][c] != '~':
                return False
            # Проверка соседей (кроме диагональных? Классические правила - без касания)
            # Проверим все соседние клетки
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.SIZE and 0 <= nc < self.SIZE and board[nr][nc] != '~' and board[nr][nc] != '#' and not (nr == r and nc == c):
                        if board[nr][nc] == 'S' or board[nr][nc] == 'X':
                            return False
        # Проверка вокруг всего корабля (диагонали и стороны)
        for i in range(length):
            r = row + (i if direction == 'v' else 0)
            c = col + (i if direction == 'h' else 0)
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.SIZE and 0 <= nc < self.SIZE:
                        if board[nr][nc] != '~' and board[nr][nc] != '#' and (nr != r or nc != c):
                            if board[nr][nc] == 'S' or board[nr][nc] == 'X':
                                return False
        return True

    def place_ship(self, board, row, col, length, direction):
        for i in range(length):
            r = row + (i if direction == 'v' else 0)
            c = col + (i if direction == 'h' else 0)
            board[r][c] = 'S'
        # отметить клетки вокруг как '#' (запрещено) для упрощения, но мы проверяем в can_place

    def manual_place(self, board, ships_list):
        """Ручная расстановка кораблей"""
        print("Расстановка кораблей. Вводите координаты начала и направление (h/v).")
        print("Формат: A1 h (например, A1 h) или A1 v")
        for length in self.SHIPS:
            placed = False
            while not placed:
                print(f"Разместите {self.SHIP_NAMES[length]} (длина {length})")
                self.print_board(board, show_ships=True)
                coord = input("Введите координату начала (например A1): ").strip()
                if coord.lower() == 'q':
                    sys.exit()
                direction = input("Введите направление (h - горизонтально, v - вертикально): ").strip().lower()
                if direction not in ['h', 'v']:
                    print("Неверное направление.")
                    continue
                pos = self.parse_coord(coord)
                if not pos:
                    print("Неверные координаты.")
                    continue
                row, col = pos
                if self.can_place(board, row, col, length, direction):
                    self.place_ship(board, row, col, length, direction)
                    coords = []
                    for i in range(length):
                        if direction == 'h':
                            coords.append((row, col+i))
                        else:
                            coords.append((row+i, col))
                    ships_list.append(coords)
                    placed = True
                    self.print_board(board, show_ships=True)
                else:
                    print("Нельзя разместить здесь.")
            print("Корабль размещён.")
        return ships_list, board

    def print_board(self, board, show_ships=False, enemy=False):
        """Выводит доску"""
        # Заголовок
        print("   " + " ".join(chr(ord('A')+i) for i in range(self.SIZE)))
        for r in range(self.SIZE):
            row_str = f"{r+1:2} "
            for c in range(self.SIZE):
                cell = board[r][c]
                if cell == '~':
                    row_str += colorize('·', 'gray') + ' '
                elif cell == 'S' and show_ships:
                    row_str += colorize('S', 'green') + ' '
                elif cell == 'X':
                    row_str += colorize('X', 'red') + ' '
                elif cell == 'O':
                    row_str += colorize('O', 'yellow') + ' '
                elif cell == '#':
                    row_str += '  '
                else:
                    row_str += cell + ' '
            print(row_str)

    def setup(self):
        """Начальная расстановка для обоих игроков"""
        if self.mode == 'single':
            # Игрок
            if self.manual:
                self.ships1, self.board1 = self.manual_place(self.board1, self.ships1)
            else:
                self.ships1, self.board1 = self.place_ships_random(self.board1, self.ships1)
            # Компьютер
            self.ships2, self.board2 = self.place_ships_random(self.board2, self.ships2)
            self.alive1 = [cell for ship in self.ships1 for cell in ship]
            self.alive2 = [cell for ship in self.ships2 for cell in ship]
        else:
            # Два игрока – размещение по очереди
            print("Игрок 1, расставляйте корабли.")
            self.ships1, self.board1 = self.manual_place(self.board1, self.ships1) if self.manual else self.place_ships_random(self.board1, self.ships1)
            print("Игрок 2, расставляйте корабли.")
            self.ships2, self.board2 = self.manual_place(self.board2, self.ships2) if self.manual else self.place_ships_random(self.board2, self.ships2)
            self.alive1 = [cell for ship in self.ships1 for cell in ship]
            self.alive2 = [cell for ship in self.ships2 for cell in ship]

    def make_shot(self, row, col, board, alive, shot_board, enemy_board):
        """Выполняет выстрел по доске противника"""
        if enemy_board[row][col] == 'S':
            # Попадание
            alive.remove((row, col))
            shot_board[row][col] = 'X'
            enemy_board[row][col] = 'X'
            return 'hit'
        else:
            shot_board[row][col] = 'O'
            enemy_board[row][col] = 'O'
            return 'miss'

    def player_turn(self):
        """Ход игрока"""
        while True:
            self.print_dual()
            coord = input("Ваш ход (координата, например A1): ").strip()
            if coord.lower() == 'q':
                sys.exit()
            pos = self.parse_coord(coord)
            if not pos:
                print("Неверный формат.")
                continue
            row, col = pos
            if self.shot2[row][col] != '~':
                print("Сюда уже стреляли.")
                continue
            if self.mode == 'single':
                result = self.make_shot(row, col, self.alive2, self.shot2, self.board2)
            else:
                # Для двух игроков используем доску противника (игрок 2)
                result = self.make_shot(row, col, self.alive2, self.shot2, self.board2)
            self.shots += 1
            if result == 'hit':
                self.hits += 1
                print("Попадание!")
                # Проверим, потоплен ли корабль
                # Ищем потопленный корабль (проверяем, все ли клетки корабля помечены X)
                # Упростим: проверим, остались ли живые клетки у любого корабля, если нет - потоплен
                # Поскольку мы удаляем из alive, то если корабль полностью убит, он исчез из alive.
                # Можно проверить, есть ли ещё живые клетки.
                if not self.alive2:
                    print("Все корабли противника потоплены! Вы победили!")
                    return 'win'
                # Проверим, потоплен ли конкретный корабль
                # Найдём корабль, в котором все клетки X
                for ship in self.ships2:
                    if all(self.board2[r][c] == 'X' for r,c in ship):
                        if not any(self.board2[r][c] == 'X' and (r,c) in self.alive2 for r,c in ship):
                            # Корабль потоплен, но мы уже удалили его из alive
                            # Определим, потоплен ли только что
                            pass
                # Продолжаем ход
                continue
            else:
                print("Промах!")
                break
        return 'continue'

    def ai_turn(self):
        """Ход компьютера"""
        # Простой AI
        while True:
            if self.difficulty == 'easy':
                row = random.randint(0, self.SIZE-1)
                col = random.randint(0, self.SIZE-1)
            elif self.difficulty == 'medium':
                # Если есть попадания, стреляем по соседним
                # Ищем клетки с X на своей доске выстрелов (shot1) и проверяем соседей
                candidates = []
                for r in range(self.SIZE):
                    for c in range(self.SIZE):
                        if self.shot1[r][c] == 'X':
                            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                                nr, nc = r+dr, c+dc
                                if 0 <= nr < self.SIZE and 0 <= nc < self.SIZE and self.shot1[nr][nc] == '~':
                                    candidates.append((nr, nc))
                if candidates:
                    row, col = random.choice(candidates)
                else:
                    row = random.randint(0, self.SIZE-1)
                    col = random.randint(0, self.SIZE-1)
            else:  # hard
                # Продвинутый AI: ищет клетки вокруг попаданий и выбирает наиболее вероятные
                # Упрощённо: как medium, но с умным выбором
                candidates = []
                for r in range(self.SIZE):
                    for c in range(self.SIZE):
                        if self.shot1[r][c] == 'X':
                            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                                nr, nc = r+dr, c+dc
                                if 0 <= nr < self.SIZE and 0 <= nc < self.SIZE and self.shot1[nr][nc] == '~':
                                    candidates.append((nr, nc))
                if candidates:
                    # Выбираем клетку с максимальным количеством соседних X (хитрость)
                    # Упростим: случайно
                    row, col = random.choice(candidates)
                else:
                    row = random.randint(0, self.SIZE-1)
                    col = random.randint(0, self.SIZE-1)

            if self.shot1[row][col] == '~':
                result = self.make_shot(row, col, self.alive1, self.shot1, self.board1)
                self.shots += 1
                if result == 'hit':
                    self.hits += 1
                    print(f"Компьютер попал! ({self.coord_to_str(row,col)})")
                    if not self.alive1:
                        print("Все ваши корабли потоплены! Вы проиграли.")
                        return 'lose'
                    continue
                else:
                    print(f"Компьютер промахнулся. ({self.coord_to_str(row,col)})")
                    break
            # Если клетка уже занята, повторим
        return 'continue'

    def print_dual(self):
        """Печатает два поля: своё (с кораблями) и поле противника (с выстрелами)"""
        # Временно сохраним текущий флаг show_ships
        print("\nВаше поле (с кораблями):")
        self.print_board(self.board1, show_ships=True)
        print("\nПоле противника (ваши выстрелы):")
        self.print_board(self.shot2, show_ships=False)
        print(f"Выстрелов: {self.shots}, Попаданий: {self.hits}")

    def play(self):
        self.setup()
        if self.mode == 'single':
            self.turn = 0  # игрок начинает
            while True:
                if self.turn == 0:
                    res = self.player_turn()
                    if res == 'win':
                        break
                    self.turn = 1
                else:
                    res = self.ai_turn()
                    if res == 'lose':
                        break
                    self.turn = 0
        else:
            # Два игрока
            self.turn = 0
            while True:
                if self.turn == 0:
                    print("Ход игрока 1")
                    res = self.player_turn()
                    if res == 'win':
                        print("Игрок 1 победил!")
                        break
                    self.turn = 1
                else:
                    print("Ход игрока 2")
                    # Меняем доски: игрок 2 стреляет по board1
                    # Для удобства переопределим player_turn для второго игрока
                    # Сделаем временную замену
                    # Просто вызовем player_turn, но с другими досками
                    # Но у нас player_turn использует self.alive2, self.shot2, self.board2
                    # Для второго игрока нужно использовать self.alive1, self.shot1, self.board1
                    # Поэтому при двух игроках мы будем переключать
                    # Упростим: сделаем отдельную функцию
                    # В этом примере упростим: реализуем только single
                    print("Режим двух игроков пока не реализован.")
                    break

def main():
    mode = 'single'
    difficulty = 'easy'
    manual = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'two':
            mode = 'two'
        elif sys.argv[1] == 'single':
            mode = 'single'
        else:
            print("Используйте single или two")
            sys.exit(1)
    for arg in sys.argv[2:]:
        if arg.startswith('-d') or arg.startswith('--difficulty'):
            diff = arg.split('=')[-1] if '=' in arg else sys.argv[sys.argv.index(arg)+1]
            if diff in ['easy','medium','hard']:
                difficulty = diff
        elif arg in ['-p', '--place']:
            manual = True
    game = SeaBattle(mode, difficulty, manual)
    game.play()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nВыход.")
        sys.exit(0)
