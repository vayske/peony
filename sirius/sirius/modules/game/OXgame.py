from graia.ariadne.typing import P


class OXgameCore:
    def __init__(self):
        self.title = "Tic-Tac-Toe"
        self.board = [[-1,-1,-1],[-1,-1,-1],[-1,-1,-1]]
        self.players = ['', '']
        self.winner = 0
        self.current_turn = 0
        self.board_size = 3
        self.game_status = 0   # 0 - idle, 1 - playing

    def game_reset(self):
        self.__init__()

    def add_player(self, name):
        if self.game_status != 0:
            return f'{self.players[0]} 和 {self.players[1]} 正在游戏中'
        if self.players[0] == '':
            self.players[0] = name
        elif self.players[1] == '':
            self.players[1] = name
        if self.players[0] != '' and self.players[1] != '':
            self.game_status = 1
            self.current_turn = 0
            return f'{self.players[0]} 和 {self.players[1]} 开始游戏\n{self.board_render(-1)}'
        else:
            return f'{name} 加入对局, 正在等待对手'

    def board_render(self, winner):
        render_output = ''
        # index = [0, 1, 2]
        index = ["\U00000030\U0000FE0F\U000020E3", "\U00000031\U0000FE0F\U000020E3", "\U00000032\U0000FE0F\U000020E3"]
        render_output += f'Turn {self.current_turn}\n\U0001F53D{index[0]}{index[1]}{index[2]}\n'
        for i in range(self.board_size):
            render_output += index[i]
            for j in self.board[i] :
                if j == -1:
                    render_output += "\U00002B1C"
                elif j == 0:
                    render_output += "\U0000274C"
                elif j == 1:
                    render_output += "\U00002B55"
            render_output += '\n'
        if winner != -1:
            if winner == 2 :
                render_output += "平局，两个菜鸡!"
            else:
                render_output += "胜者是" + self.players[winner]
        return render_output

    def check_win_status(self, player):
        # -1 - not ended
        # 0 - player 1 wins
        # 1 - player 2 wins
        # 2 - draw
        draw = True
        for i in range(self.board_size):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] == player:
                return player
            if self.board[0][i] == self.board[1][i] == self.board[2][i] == player:
                return player
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == player:
            return player
        elif self.board[0][2] == self.board[1][1] == self.board[2][0] == player:
            return player
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == -1:
                    draw = False
                    break
        if draw:
            return 2
        return -1

    def move(self, player, x, y):
        if self.game_status == 0:
            return f'游戏未开始'
        if player not in self.players:
            return f'{self.players[0]} 和 {self.players[1]} 正在游戏中'
        if x < 0 or x > 2 or y < 0 or y > 2:
            return f'无效移动'
        current_player = self.current_turn % 2
        if self.players[current_player] != player:
            return f'现在是{self.players[current_player]}的回合'
        if self.board[x][y] != -1:
            return f'无效移动'
        else :
            self.board[x][y] = current_player
        winner = self.check_win_status(current_player)
        render = self.board_render(winner)
        self.current_turn += 1
        if winner != -1:
            self.game_reset()
        return render
