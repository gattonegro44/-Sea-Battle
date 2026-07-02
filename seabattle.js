// seabattle.js
#!/usr/bin/env node
'use strict';

const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const COLORS = {
    reset: '\x1b[0m',
    blue: '\x1b[94m',
    green: '\x1b[92m',
    red: '\x1b[91m',
    yellow: '\x1b[93m',
    cyan: '\x1b[96m',
    gray: '\x1b[90m',
    bold: '\x1b[1m'
};

function colorize(text, color) {
    return COLORS[color] + text + COLORS.reset;
}

const SIZE = 10;
const SHIP_LENGTHS = [4,3,3,2,2,2,1,1,1,1];

class SeaBattle {
    constructor(mode, difficulty, manual) {
        this.mode = mode;
        this.difficulty = difficulty;
        this.manual = manual;
        this.board1 = Array.from({length:SIZE}, () => Array(SIZE).fill('~'));
        this.board2 = Array.from({length:SIZE}, () => Array(SIZE).fill('~'));
        this.shot1 = Array.from({length:SIZE}, () => Array(SIZE).fill('~'));
        this.shot2 = Array.from({length:SIZE}, () => Array(SIZE).fill('~'));
        this.ships1 = [];
        this.ships2 = [];
        this.alive1 = [];
        this.alive2 = [];
        this.shots = 0;
        this.hits = 0;
        this.turn = 0;
    }

    parseCoord(s) {
        const m = s.match(/^([A-Ja-j])(\d{1,2})$/);
        if (!m) return null;
        const col = m[1].toUpperCase().charCodeAt(0) - 65;
        const row = parseInt(m[2]) - 1;
        if (row < 0 || row >= SIZE || col < 0 || col >= SIZE) return null;
        return [row, col];
    }

    coordStr(r,c) {
        return String.fromCharCode(65+c) + (r+1);
    }

    canPlace(board, row, col, length, dir) {
        for (let i=0; i<length; i++) {
            let r = dir==='v' ? row+i : row;
            let c = dir==='h' ? col+i : col;
            if (r>=SIZE || c>=SIZE || board[r][c] !== '~') return false;
            for (let dr=-1; dr<=1; dr++) {
                for (let dc=-1; dc<=1; dc++) {
                    let nr=r+dr, nc=c+dc;
                    if (nr>=0 && nr<SIZE && nc>=0 && nc<SIZE && board[nr][nc] !== '~' && board[nr][nc] !== '#') {
                        if (board[nr][nc] === 'S' || board[nr][nc] === 'X') return false;
                    }
                }
            }
        }
        return true;
    }

    placeShip(board, row, col, length, dir) {
        for (let i=0; i<length; i++) {
            let r = dir==='v' ? row+i : row;
            let c = dir==='h' ? col+i : col;
            board[r][c] = 'S';
        }
    }

    placeRandom(board, ships) {
        for (const length of SHIP_LENGTHS) {
            let placed = false;
            let attempts = 0;
            while (!placed && attempts < 1000) {
                attempts++;
                let row = Math.floor(Math.random()*SIZE);
                let col = Math.floor(Math.random()*SIZE);
                let dir = Math.random()<0.5 ? 'h' : 'v';
                if (this.canPlace(board, row, col, length, dir)) {
                    this.placeShip(board, row, col, length, dir);
                    let coords = [];
                    for (let i=0; i<length; i++) {
                        let r = dir==='v' ? row+i : row;
                        let c = dir==='h' ? col+i : col;
                        coords.push([r,c]);
                    }
                    ships.push(coords);
                    placed = true;
                }
            }
            if (!placed) {
                for (let i=0; i<SIZE; i++) board[i].fill('~');
                ships.length = 0;
                this.placeRandom(board, ships);
                return;
            }
        }
    }

    manualPlace(board, ships) {
        return new Promise((resolve) => {
            console.log('Ручная расстановка кораблей.');
            const placeNext = (idx) => {
                if (idx >= SHIP_LENGTHS.length) { resolve(); return; }
                const length = SHIP_LENGTHS[idx];
                console.log(`Разместите корабль длины ${length}`);
                this.printBoard(board, true);
                rl.question('Введите координату (A1): ', (coord) => {
                    if (coord === 'q') process.exit();
                    rl.question('Введите направление (h/v): ', (dir) => {
                        const pos = this.parseCoord(coord);
                        if (!pos || (dir !== 'h' && dir !== 'v')) {
                            console.log('Неверный ввод.');
                            placeNext(idx);
                            return;
                        }
                        const [row, col] = pos;
                        if (this.canPlace(board, row, col, length, dir)) {
                            this.placeShip(board, row, col, length, dir);
                            let coords = [];
                            for (let i=0; i<length; i++) {
                                let r = dir==='v' ? row+i : row;
                                let c = dir==='h' ? col+i : col;
                                coords.push([r,c]);
                            }
                            ships.push(coords);
                            console.log('Корабль размещён.');
                            placeNext(idx+1);
                        } else {
                            console.log('Нельзя разместить здесь.');
                            placeNext(idx);
                        }
                    });
                });
            };
            placeNext(0);
        });
    }

    printBoard(board, showShips=false) {
        process.stdout.write('   ');
        for (let i=0; i<SIZE; i++) process.stdout.write(String.fromCharCode(65+i) + ' ');
        console.log();
        for (let r=0; r<SIZE; r++) {
            process.stdout.write((r+1).toString().padStart(2) + ' ');
            for (let c=0; c<SIZE; c++) {
                const cell = board[r][c];
                if (cell === '~') process.stdout.write(colorize('· ', 'gray'));
                else if (cell === 'S' && showShips) process.stdout.write(colorize('S ', 'green'));
                else if (cell === 'X') process.stdout.write(colorize('X ', 'red'));
                else if (cell === 'O') process.stdout.write(colorize('O ', 'yellow'));
                else process.stdout.write(cell + ' ');
            }
            console.log();
        }
    }

    makeShot(row, col, alive, shotBoard, enemyBoard) {
        if (enemyBoard[row][col] === 'S') {
            const idx = alive.findIndex(p => p[0]===row && p[1]===col);
            if (idx !== -1) alive.splice(idx,1);
            shotBoard[row][col] = 'X';
            enemyBoard[row][col] = 'X';
            return 'X';
        } else {
            shotBoard[row][col] = 'O';
            enemyBoard[row][col] = 'O';
            return 'O';
        }
    }

    printDual() {
        console.log('\nВаше поле:');
        this.printBoard(this.board1, true);
        console.log('\nПоле противника:');
        this.printBoard(this.shot2, false);
        console.log(`Выстрелов: ${this.shots}, Попаданий: ${this.hits}`);
    }

    playerTurn() {
        return new Promise((resolve) => {
            const ask = () => {
                this.printDual();
                rl.question('Ваш ход (A1): ', (coord) => {
                    if (coord === 'q') process.exit();
                    const pos = this.parseCoord(coord);
                    if (!pos) {
                        console.log('Неверный формат.');
                        ask();
                        return;
                    }
                    const [row, col] = pos;
                    if (this.shot2[row][col] !== '~') {
                        console.log('Сюда уже стреляли.');
                        ask();
                        return;
                    }
                    const res = this.makeShot(row, col, this.alive2, this.shot2, this.board2);
                    this.shots++;
                    if (res === 'X') {
                        this.hits++;
                        console.log('Попадание!');
                        if (this.alive2.length === 0) {
                            console.log('Все корабли противника потоплены! Вы победили!');
                            resolve(1);
                            return;
                        }
                        ask(); // continue
                    } else {
                        console.log('Промах.');
                        resolve(0);
                    }
                });
            };
            ask();
        });
    }

    aiTurn() {
        return new Promise((resolve) => {
            let row, col;
            if (this.difficulty === 'easy') {
                row = Math.floor(Math.random()*SIZE);
                col = Math.floor(Math.random()*SIZE);
            } else {
                let candidates = [];
                for (let r=0; r<SIZE; r++)
                    for (let c=0; c<SIZE; c++)
                        if (this.shot1[r][c] === 'X') {
                            for (const [dr,dc] of [[1,0],[-1,0],[0,1],[0,-1]]) {
                                let nr=r+dr, nc=c+dc;
                                if (nr>=0 && nr<SIZE && nc>=0 && nc<SIZE && this.shot1[nr][nc] === '~')
                                    candidates.push([nr,nc]);
                            }
                        }
                if (candidates.length) {
                    const idx = Math.floor(Math.random()*candidates.length);
                    [row,col] = candidates[idx];
                } else {
                    row = Math.floor(Math.random()*SIZE);
                    col = Math.floor(Math.random()*SIZE);
                }
            }
            if (this.shot1[row][col] === '~') {
                const res = this.makeShot(row, col, this.alive1, this.shot1, this.board1);
                this.shots++;
                if (res === 'X') {
                    this.hits++;
                    console.log(`Компьютер попал! (${this.coordStr(row,col)})`);
                    if (this.alive1.length === 0) {
                        console.log('Все ваши корабли потоплены! Вы проиграли.');
                        resolve(-1);
                        return;
                    }
                    // continue AI turn
                    setTimeout(() => this.aiTurn().then(resolve), 100);
                } else {
                    console.log(`Компьютер промахнулся. (${this.coordStr(row,col)})`);
                    resolve(0);
                }
            } else {
                this.aiTurn().then(resolve);
            }
        });
    }

    async setup() {
        if (this.mode === 'single') {
            if (this.manual) {
                await this.manualPlace(this.board1, this.ships1);
            } else {
                this.placeRandom(this.board1, this.ships1);
            }
            this.placeRandom(this.board2, this.ships2);
            this.alive1 = this.ships1.flat();
            this.alive2 = this.ships2.flat();
        } else {
            console.log('Режим двух игроков пока не реализован.');
        }
    }

    async play() {
        await this.setup();
        if (this.mode === 'single') {
            while (true) {
                if (this.turn === 0) {
                    const res = await this.playerTurn();
                    if (res === 1) break;
                    this.turn = 1;
                } else {
                    const res = await this.aiTurn();
                    if (res === -1) break;
                    this.turn = 0;
                }
            }
        }
    }
}

async function main() {
    let mode = 'single', difficulty = 'easy', manual = false;
    const args = process.argv.slice(2);
    if (args.length && args[0] === 'two') mode = 'two';
    for (let i=1; i<args.length; i++) {
        if (args[i] === '-d' || args[i] === '--difficulty') {
            if (i+1 < args.length) difficulty = args[++i];
        } else if (args[i] === '-p' || args[i] === '--place') {
            manual = true;
        }
    }
    const game = new SeaBattle(mode, difficulty, manual);
    await game.play();
    rl.close();
}

main();
