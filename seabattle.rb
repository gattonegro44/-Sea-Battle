#!/usr/bin/env ruby
# seabattle.rb
# encoding: UTF-8

require 'set'

COLORS = {
  reset: "\e[0m",
  blue: "\e[94m",
  green: "\e[92m",
  red: "\e[91m",
  yellow: "\e[93m",
  gray: "\e[90m"
}

def colorize(text, color)
  "#{COLORS[color]}#{text}#{COLORS[:reset]}"
end

SIZE = 10
SHIP_LENGTHS = [4,3,3,2,2,2,1,1,1,1]

class SeaBattle
  attr_reader :mode, :difficulty, :manual

  def initialize(mode, difficulty, manual)
    @mode = mode
    @difficulty = difficulty
    @manual = manual
    @board1 = Array.new(SIZE) { Array.new(SIZE, '~') }
    @board2 = Array.new(SIZE) { Array.new(SIZE, '~') }
    @shot1 = Array.new(SIZE) { Array.new(SIZE, '~') }
    @shot2 = Array.new(SIZE) { Array.new(SIZE, '~') }
    @ships1 = []
    @ships2 = []
    @alive1 = Set.new
    @alive2 = Set.new
    @shots = 0
    @hits = 0
    @turn = 0
  end

  def parse_coord(s)
    return nil unless s =~ /^([A-Ja-j])(\d{1,2})$/
    col = $1.upcase.ord - 'A'.ord
    row = $2.to_i - 1
    return nil if row < 0 || row >= SIZE || col < 0 || col >= SIZE
    [row, col]
  end

  def coord_str(r, c)
    "#{(c+'A'.ord).chr}#{r+1}"
  end

  def can_place(board, row, col, length, dir)
    (0...length).each do |i|
      r = dir == 'v' ? row+i : row
      c = dir == 'h' ? col+i : col
      return false if r >= SIZE || c >= SIZE || board[r][c] != '~'
      (-1..1).each do |dr|
        (-1..1).each do |dc|
          nr, nc = r+dr, c+dc
          next unless nr >= 0 && nr < SIZE && nc >= 0 && nc < SIZE
          next if board[nr][nc] == '~' || board[nr][nc] == '#'
          return false if board[nr][nc] == 'S' || board[nr][nc] == 'X'
        end
      end
    end
    true
  end

  def place_ship(board, row, col, length, dir)
    (0...length).each do |i|
      r = dir == 'v' ? row+i : row
      c = dir == 'h' ? col+i : col
      board[r][c] = 'S'
    end
  end

  def place_random(board, ships)
    length = SHIP_LENGTHS.first
    while !SHIP_LENGTHS.empty?
      length = SHIP_LENGTHS.shift
      placed = false
      attempts = 0
      while !placed && attempts < 1000
        attempts += 1
        row, col = rand(SIZE), rand(SIZE)
        dir = ['h','v'].sample
        if can_place(board, row, col, length, dir)
          place_ship(board, row, col, length, dir)
          coords = (0...length).map do |i|
            r = dir == 'v' ? row+i : row
            c = dir == 'h' ? col+i : col
            [r,c]
          end
          ships << coords
          placed = true
        end
      end
      if !placed
        (0...SIZE).each { |i| (0...SIZE).each { |j| board[i][j] = '~' } }
        ships.clear
        return place_random(board, ships)
      end
    end
  end

  def manual_place(board, ships)
    puts "Ручная расстановка кораблей."
    SHIP_LENGTHS.each do |length|
      placed = false
      while !placed
        puts "Разместите корабль длины #{length}"
        print_board(board, true)
        print "Введите координату (A1): "
        coord = gets.chomp
        exit if coord == 'q'
        print "Введите направление (h/v): "
        dir = gets.chomp
        pos = parse_coord(coord)
        unless pos && ['h','v'].include?(dir)
          puts "Неверный ввод."
          next
        end
        row, col = pos
        if can_place(board, row, col, length, dir)
          place_ship(board, row, col, length, dir)
          coords = (0...length).map do |i|
            r = dir == 'v' ? row+i : row
            c = dir == 'h' ? col+i : col
            [r,c]
          end
          ships << coords
          placed = true
        else
          puts "Нельзя разместить здесь."
        end
      end
    end
  end

  def print_board(board, show_ships=false)
    print "   "
    (0...SIZE).each { |i| print "#{(65+i).chr} " }
    puts
    (0...SIZE).each do |r|
      print "#{r+1} "
      (0...SIZE).each do |c|
        cell = board[r][c]
        if cell == '~'
          print colorize("· ", :gray)
        elsif cell == 'S' && show_ships
          print colorize("S ", :green)
        elsif cell == 'X'
          print colorize("X ", :red)
        elsif cell == 'O'
          print colorize("O ", :yellow)
        else
          print cell + " "
        end
      end
      puts
    end
  end

  def make_shot(row, col, alive, shot_board, enemy_board)
    if enemy_board[row][col] == 'S'
      alive.delete([row,col])
      shot_board[row][col] = 'X'
      enemy_board[row][col] = 'X'
      'X'
    else
      shot_board[row][col] = 'O'
      enemy_board[row][col] = 'O'
      'O'
    end
  end

  def print_dual
    puts "\nВаше поле:"
    print_board(@board1, true)
    puts "\nПоле противника:"
    print_board(@shot2, false)
    puts "Выстрелов: #{@shots}, Попаданий: #{@hits}"
  end

  def player_turn
    loop do
      print_dual
      print "Ваш ход (A1): "
      coord = gets.chomp
      exit if coord == 'q'
      pos = parse_coord(coord)
      unless pos
        puts "Неверный формат."
        next
      end
      row, col = pos
      if @shot2[row][col] != '~'
        puts "Сюда уже стреляли."
        next
      end
      res = make_shot(row, col, @alive2, @shot2, @board2)
      @shots += 1
      if res == 'X'
        @hits += 1
        puts "Попадание!"
        if @alive2.empty?
          puts "Все корабли противника потоплены! Вы победили!"
          return 1
        end
        next
      else
        puts "Промах."
        break
      end
    end
    0
  end

  def ai_turn
    loop do
      if @difficulty == 'easy'
        row = rand(SIZE)
        col = rand(SIZE)
      else
        candidates = []
        (0...SIZE).each do |r|
          (0...SIZE).each do |c|
            if @shot1[r][c] == 'X'
              [[1,0],[-1,0],[0,1],[0,-1]].each do |dr,dc|
                nr, nc = r+dr, c+dc
                if nr>=0 && nr<SIZE && nc>=0 && nc<SIZE && @shot1[nr][nc] == '~'
                  candidates << [nr,nc]
                end
              end
            end
          end
        end
        if candidates.any?
          row, col = candidates.sample
        else
          row = rand(SIZE)
          col = rand(SIZE)
        end
      end
      if @shot1[row][col] == '~'
        res = make_shot(row, col, @alive1, @shot1, @board1)
        @shots += 1
        if res == 'X'
          @hits += 1
          puts "Компьютер попал! (#{coord_str(row,col)})"
          if @alive1.empty?
            puts "Все ваши корабли потоплены! Вы проиграли."
            return -1
          end
          next
        else
          puts "Компьютер промахнулся. (#{coord_str(row,col)})"
          break
        end
      end
    end
    0
  end

  def setup
    if @mode == 'single'
      if @manual
        manual_place(@board1, @ships1)
      else
        place_random(@board1, @ships1)
      end
      place_random(@board2, @ships2)
      @alive1 = @ships1.flatten(1).to_set
      @alive2 = @ships2.flatten(1).to_set
    else
      puts "Режим двух игроков пока не реализован."
    end
  end

  def play
    setup
    if @mode == 'single'
      loop do
        if @turn == 0
          res = player_turn
          break if res == 1
          @turn = 1
        else
          res = ai_turn
          break if res == -1
          @turn = 0
        end
      end
    end
  end
end

def main
  mode = 'single'
  difficulty = 'easy'
  manual = false
  if ARGV.size > 0 && ARGV[0] == 'two'
    mode = 'two'
  end
  (1...ARGV.size).each do |i|
    if ARGV[i] == '-d' || ARGV[i] == '--difficulty'
      difficulty = ARGV[i+1] if i+1 < ARGV.size
    elsif ARGV[i] == '-p' || ARGV[i] == '--place'
      manual = true
    end
  end
  game = SeaBattle.new(mode, difficulty, manual)
  game.play
end

main if __FILE__ == $0
