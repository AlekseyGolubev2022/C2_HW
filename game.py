"""Игра "Морской бой" (1 игрок с компьютером)."""
# Т.к. тема ООП, в классы объединаются соответствующие им данные и методы.

import random

N = 6  # размер игрового поля (рабочие варианты: 6)
scope = tuple(i for i in range(N))  # диапазон координат


class Ship:
    """Класс определяет корабль игрока, размер, кординаты, статус
    и методы для ввода координат, изменения/получения статуса.
    """
    def __init__(self, size, coords):
        self.__size = size
        self.__coords = coords
        self.__hits = 0

    @property
    def size(self):
        return self.__size

    @property
    def coords(self):
        return self.__coords

    @property
    def hits(self):
        return self.__hits

    @hits.setter
    def hits(self, value):
        self.__hits = value

    @property
    def status(self):
        if self.__hits == self.__size: 
            self.__status = 'уничтожен'
        elif self.__hits > 0:
            self.__status = 'поврежден'
        else:
            self.__status = 'не поврежден'
        return self.__status


class Board:
    """Класс игрового поля. Определяет экз.игрового поля игрока,
    и методы в т.ч. создание, размещение, ввод хода, проверка, отображение.   
    Обозначения в соответствии с Заданием:
    О - (рус.О) пустая клетка (и корабли/части при визуализации чужого поля)
    ■ - корабль/часть
    X - (лат.X) попадание
    T - (лат.T) промах
    """
#---------------------------------------79------------------------------------ 
    def __init__(self, player):
        self._player = player

    @property
    def grid(self):
        return self.__grid

    @grid.setter
    def grid(self, value):
        self.__grid = value
      
    def around(self, i, j):
        """Проверка области (точка + периметр)."""
        all = [(y, x) for y in (i - 1, i, i + 1) for x in (j - 1, j, j + 1)]
        all_in_scope = filter(lambda x: {x[0], x[1]}.issubset(scope), all)
        if set([self.grid[i[0]][i[1]] for i in all_in_scope]) == {'О'}:
            return True

    # Т.к. в задании прямо не оговорено, размещение кораблей автоматическое
    def autoplace(self):
        self.grid = [['О' for i in range(N)] for j in range(N)]
        self.ships = []

        def place_ship(size):
            counter = 0
            while True:
                counter += 1
                if counter > 20:
                    raise ValueError('Неподходящее расположение кораблей')
                coords = []
                i, j = random.randint(0,5), random.randint(0,5)
                if self.grid[i][j] != 'О':
                    continue
                if not self.around(i, j):
                    continue
                coords.append((i, j))

                s = scope
                if size > 1:
                    choices_i = [(i + d, j) for d in (-1, 1) if (i + d) in s]
                    choices_j = [(i, j + d) for d in (-1, 1) if (j + d) in s]
                    point_2 = random.choice(choices_i + choices_j)
                    i, j = point_2[0], point_2[1]
                    if self.grid[i][j] != 'О':
                        continue
                    if not self.around(i, j):
                        continue
                    coords.append(point_2)

                if size == 3:
                    di = coords[1][0] - coords[0][0]
                    dj = coords[1][1] - coords[0][1]
                    if di:
                        inline = [(i + d, j) for d in (-2 * di, di)
                                  if (i + d) in s]
                    else:
                        inline = [(i, j + d) for d in (-2 * dj, dj)
                                  if (j + d) in s]
                    point_3 = random.choice(inline)
                    i, j = point_3[0], point_3[1]
                    if self.grid[i][j] != 'О':
                        continue
                    if not self.around(i, j):
                        continue
                    coords.append(point_3)

                for i in coords:
                    self.grid[i[0]][i[1]] = '■'
                ship = Ship(size, coords)
                self.ships.append(ship)
                print(f'Добавлен корабль (размер {size}, игрок {self._player})')
                break

        while True:
            try:
                for size in (3, 2, 2, 1, 1, 1, 1):
                    place_ship(size)
            except ValueError:
                print('Неподходящее расположение кораблей')
                self.grid = [['О' for i in range(N)] for j in range(N)]
                self.ships = []
                continue
            p = self._player
            print(f'\n--- Авторазмещение кораблей ({p}) успешно завершено ---')
            break

    def shoot(self):
        atacker = 'player_AI' if self._player == 'player_1' else 'player_1'
        print(f'\n=== Выстрел игрока {atacker} по полю {self._player}.===')
        print('Введите через пробел № строки и № столбца')
        while True:
            try:
                if atacker == 'player_AI':
                    #row, column = random.randint(0,5), random.randint(0,5)
                    shot = (random.randint(0,5), random.randint(0,5))
                else:
                    shot = tuple(map(lambda x: int(x) - 1, input().split()))
                if len(shot) != 2:
                    raise TypeError
            except (TypeError, ValueError) as e:
                print(type(e), ' Неверный формат. Введите заново (2 числа): ')
                continue
            if not (shot[0] in scope and shot[1] in scope):
                print('Неверный формат (диапазон). Введите заново: ')
                continue
            target = self.grid[shot[0]][shot[1]]
            if target in ('T', 'X'):
                print('Нельзя дважды бить в 1 точку. Введите заново: ')
                continue
            self.grid[shot[0]][shot[1]] = 'X' if target == '■' else 'T'
            view = tuple(map(lambda x: x+1, shot))
            self.bonus_step = False
            if target == '■':
                ship = list(filter(lambda x: shot in x.coords, self.ships))
                ship[0].hits += 1
                state = f'Ход{view}- корабль {ship[0].status}! дается +1 ход!'
                self.bonus_step = True
            print(state) if target == '■' else print(f'Ход{view}- мимо')
            break


def game_1_player():
    print('\n---------- НОВАЯ ИГРА ---------- (смотрите схему).')
    print('Примечания: кто делает 1й ход - определяется случайным образом,')
    print('при попадании сообщается статус, и дается еще 1 ход вне очереди,')
    print('корабли размещаются в линию по горизонтали или вертикали ')
    print('на расстоянии минимум через 1 клетку, включая диагональное.')
    print('\n' + 'Расстановка кораблей случайная автоматическая.')

    board_p1 = Board('player_1')
    board_p1.autoplace()
    board_AI = Board('player_AI')
    board_AI.autoplace()
    
    def print_board(board):
        print(f'\n-----Игровое поле кораблей игрока {board._player}-----')
        print(f'  | {" | ".join(str(j+1) for j in range(N))} |')
        for i in range(N):
            data = " | ".join(board.grid[i][j] for j in range(N))
            if board._player == 'player_AI':
                data = data.replace('■', 'О')    
            print(f'{i+1} | {data} |')

    def game_over(board):
        if '■' not in [i for j in board.grid for i in j]:
            return True

    atacker = 'player_1'
    next_a = 'player_AI'
    if random.randint(0,1) == 0:
        atacker, next_a = next_a, atacker
    while True:
        if atacker == 'player_1':
            print_board(board_p1)
            print_board(board_AI)
        board_AI.shoot() if atacker == 'player_1' else board_p1.shoot()
        board = board_AI if atacker == 'player_1' else board_p1
        if game_over(board):
            print(f'\n-----Игра закончена. Выиграл {atacker} !-----')
            break
        if not board.bonus_step:
            atacker, next_a = next_a, atacker
    new()
  

def new():
    new_game = input('\n' + 'Новая игра? (y/n) (по умолчанию "y")): ')
    print('(прервать - "ctrl+c", перезапуск - "new()")')
    if new_game not in ('n', 'N'):
        game_1_player()


new()
