from neyro import *
import json
import random
class Qlerning:
    def __init__(self, size, agent, N, a = 0.1, y = 0.9, url = ''):
        self.agent = agent
        self.N = N
        self.a = a
        self.y = y
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.eps = 1.0
        self.Q = []
        self.color = ''
        self.score = []
        self.inf = []
        self.play = False
        self.url = url
        
    def update_weight(self, inf, r): # Обновляет веса (Q-lerning)
        self.Q[inf[0]][3][inf[1]] += self.a * (r + self.y * max(self.Q[inf[2]][3]) - self.Q[inf[0]][3][inf[1]])

    def prov(self, q): #Проверка наличия состояния в матрице и добавление если нет
        for i in range(len(self.Q)):
            if self.Q[i][:3] == q[:3]:
                return i
        if not self.play:
            self.Q.append([])
            self.Q[-1].append(q[0])
            self.Q[-1].append([])
            for i in q[1]:
                self.Q[-1][1].append(i.copy())
            self.Q[-1].append(q[2].copy())
            self.Q[-1].append(q[3].copy())
            return len(self.Q) - 1
        else:
            return -1
            
    def reform(self, board, slov): # Преобразование доски, и списка для использования в матрице
        new_slov = []
        prikol = []
        for i in slov:
            for j in slov[i]:
                new_slov.append(i+j)
                prikol.append(0.0)
        return [self.color, board, new_slov, prikol]

    def reward(self, score): # Вознаграждение
        if len(self.score) == 0:
            r = 0
            self.score = score
        else:
            r = score[0] - self.score[0] + self.score[1] - score[1]
            self.score = score
        return r
    
    def rand(self, board, slov, q):
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        self.inf.append(q[2].index(pawn + move))
        return (pawn, move)

    def greedy(self, board, slov, q):
        weigth = {}
        for i in slov:
            count = 0
            z = []
            for j in range(len(self.Q[self.inf[0]][2])):
                if self.Q[self.inf[0]][2][j][:2] == i:
                    count+=1
                    z.append(self.Q[self.inf[0]][3][j])
                if count == len(slov[i]):
                    break
            weigth.update({i:z})
        best = {}
        t = str(slov.keys())
        keys = t[12:len(t)-3].split("', '")
        mx = float('-inf')
        for i in keys:
            boy = False
            for j in range(len(slov[i])):
                try:
                    if weigth[i][j] > mx:
                        best = {i:[slov[i][j]]}
                        mx = weigth[i][j]
                        boy = True
                    elif weigth[i][j] == mx and boy:
                        best[i].append(slov[i][j])
                    elif weigth[i][j] == mx and not boy:
                        best.update({i:[slov[i][j]]})
                except:
                    print(weigth, i, j)
                    exit(52)
        return self.rand(board, best, q)
                
    def chose_action(self, board, slov, score, c = 0): # Выбор действия (рандомно или по умному)
        q = self.reform(board, slov)
        if not self.play:
            self.inf.append(self.prov(q))
            r = self.reward(score)
            if len(self.inf) > 2:
                self.update_weight(self.inf, r)
                for i in range(2):
                    self.inf.pop(0)
            rand = random.random()
            if rand <= self.eps:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
        else:
            self.inf = [self.prov(q)]
            if self.inf[0] == -1:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
            
    
    def game(self, n):
        game = Environment(self.size)
        player = Players(game, self.url)
        if self.agent == 'usefulness':
            agent = player.usefulness_agent
        elif self.agent == 'greedy':
            agent = player.agent_greedy
        else:
            agent = player.agent_rand
        if n % 2 == 0:
            self.color = 'BK'
            (board, score, color) = game.env(agent, self.chose_action)
        else:
            self.color = 'WC'
            (board, score, color) = game.env(self.chose_action, agent)
        if color != self.color:
            m = score[1]
            score[1] = score[0]
            score[0] = m
        slov = {'52': ['52']}
        q = self.reform(board, slov)
        self.inf.append(self.prov(q))
        self.update_weight(self.inf, self.reward(score))
        self.eps -= 1.0 / self.N
        self.score = []
        self.inf = []

    def lerning(self, progress = False, agent = 'null', N = 'null', a = 'null', y = 'null', eps = 'null'):
        if agent != 'null': self.agent = agent
        if eps != 'null': self.eps = eps
        if N != 'null': self.N = N
        if a != 'null': self.a = a
        if y != 'null': self.y = y
        lasteps = self.eps
        for i in range(self.N):
            if lasteps - self.eps > 0.01 and progress:
                lasteps -= 0.01
                print('Прогресс: ' + str(int((1 - lasteps)*100)) + '%')
            self.epz = 0
            self.game(i)

    def win_rate(self, N, agent):
        count = 0
        win = 0
        self.play = True
        for n in range(N):
            game = Environment(self.size)
            player = Players(game, self.url)
            if self.agent == 'usefulness':
                agent = player.usefulness_agent
            elif self.agent == 'greedy':
                agent = player.agent_greedy
            else:
                agent = player.agent_rand
            if n % 2 == 0:
                self.color = 'BK'
                (board, score, color) = game.env(agent, self.chose_action)
            else:
                self.color = 'WC'
                (board, score, color) = game.env(self.chose_action, agent)
            if self.color == color:
                win+=1
            count+=1
        self.play = False
        self.inf = []
        return round(win/count, 2)

    def save(self, file):
        if file[-5:] != '.json':
            return False
        with open(file, 'w') as json_file:
            json.dump(self.Q, json_file)
        return True
    
    def print_weights(self):
        for i in self.Q:
            print(i[0])
            print('-----------------------')
            c = 1
            for j in i[1]:
                c+=1
                print(*j, end = ' ')
                print('|', end = ' ')
                if c <= 3:
                    print(*i[c])
                else:
                    print()
            print()
#------------------------------------------------------------------------
class Sarsa:
    def __init__(self, size, agent, N, a = 0.1, y = 0.9, url = ''):
        self.agent = agent
        self.N = N
        self.a = a
        self.y = y
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.eps = 1.0
        self.Q = []
        self.color = ''
        self.score = []
        self.inf = []
        self.play = False
        self.url = url
        
    def update_weight(self, inf, r): # Обновляет веса (Sarsa)
        self.Q[inf[0]][3][inf[1]] += self.a * (r + self.y * sum(self.Q[inf[2]][3])/len(self.Q[inf[2]][3]) - self.Q[inf[0]][3][inf[1]])

    def prov(self, q): #Проверка наличия состояния в матрице и добавление если нет
        for i in range(len(self.Q)):
            if self.Q[i][:3] == q[:3]:
                return i
        if not self.play:
            self.Q.append([])
            self.Q[-1].append(q[0])
            self.Q[-1].append([])
            for i in q[1]:
                self.Q[-1][1].append(i.copy())
            self.Q[-1].append(q[2].copy())
            self.Q[-1].append(q[3].copy())
            return len(self.Q) - 1
        else:
            return -1
            
    def reform(self, board, slov): # Преобразование доски, и списка для использования в матрице
        new_slov = []
        prikol = []
        for i in slov:
            for j in slov[i]:
                new_slov.append(i+j)
                prikol.append(0.0)
        return [self.color, board, new_slov, prikol]

    def reward(self, score): # Вознаграждение
        if len(self.score) == 0:
            r = 0
            self.score = score
        else:
            r = score[0] - self.score[0] + self.score[1] - score[1]
            self.score = score
        return r
    
    def rand(self, board, slov, q):
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        self.inf.append(q[2].index(pawn + move))
        return (pawn, move)

    def greedy(self, board, slov, q):
        weigth = {}
        for i in slov:
            count = 0
            z = []
            for j in range(len(self.Q[self.inf[0]][2])):
                if self.Q[self.inf[0]][2][j][:2] == i:
                    count+=1
                    z.append(self.Q[self.inf[0]][3][j])
                if count == len(slov[i]):
                    break
            weigth.update({i:z})
        best = {}
        t = str(slov.keys())
        keys = t[12:len(t)-3].split("', '")
        mx = float('-inf')
        for i in keys:
            boy = False
            for j in range(len(slov[i])):
                if weigth[i][j] > mx:
                    best = {i:[slov[i][j]]}
                    mx = weigth[i][j]
                    boy = True
                elif weigth[i][j] == mx and boy:
                    best[i].append(slov[i][j])
                elif weigth[i][j] == mx and not boy:
                    best.update({i:[slov[i][j]]})
        return self.rand(board, best, q)
                
    def chose_action(self, board, slov, score, c = 0): # Выбор действия (рандомно или по умному)
        q = self.reform(board, slov)
        if not self.play:
            self.inf.append(self.prov(q))
            r = self.reward(score)
            if len(self.inf) > 2:
                self.update_weight(self.inf, r)
                for i in range(2):
                    self.inf.pop(0)
            rand = random.random()
            if rand <= self.eps:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
        else:
            self.inf = [self.prov(q)]
            if self.inf[0] == -1:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
            
    
    def game(self, n):
        game = Environment(self.size)
        player = Players(game, self.url)
        if self.agent == 'usefulness':
            agent = player.usefulness_agent
        elif self.agent == 'greedy':
            agent = player.agent_greedy
        else:
            agent = player.agent_rand
        if n % 2 == 0:
            self.color = 'BK'
            (board, score, color) = game.env(agent, self.chose_action)
        else:
            self.color = 'WC'
            (board, score, color) = game.env(self.chose_action, agent)
        if color != self.color:
            m = score[1]
            score[1] = score[0]
            score[0] = m
        slov = {'52': ['52']}
        q = self.reform(board, slov)
        self.inf.append(self.prov(q))
        self.update_weight(self.inf, self.reward(score))
        self.eps -= 1.0 / self.N
        self.score = []
        self.inf = []

    def lerning(self, progress = False, agent = 'null', N = 'null', a = 'null', y = 'null', eps = 'null'):
        if agent != 'null': self.agent = agent
        if eps != 'null': self.eps = eps
        if N != 'null': self.N = N
        if a != 'null': self.a = a
        if y != 'null': self.y = y
        lasteps = self.eps
        for i in range(self.N):
            if lasteps - self.eps > 0.01 and progress:
                lasteps -= 0.01
                print('Прогресс: ' + str(int((1 - lasteps)*100)) + '%')
            self.game(i)

    def win_rate(self, N, agent):
        count = 0
        win = 0
        self.play = True
        for n in range(N):
            game = Environment(self.size)
            player = Players(game, self.url)
            if self.agent == 'usefulness':
                agent = player.usefulness_agent
            elif self.agent == 'greedy':
                agent = player.agent_greedy
            else:
                agent = player.agent_rand
            if n % 2 == 0:
                self.color = 'BK'
                (board, score, color) = game.env(agent, self.chose_action)
            else:
                self.color = 'WC'
                (board, score, color) = game.env(self.chose_action, agent)
            if self.color == color:
                win+=1
            count+=1
        self.play = False
        self.inf = []
        return round(win/count, 2)

    def save(self, file):
        if file[-5:] != '.json':
            return False
        with open(file, 'w') as json_file:
            json.dump(self.Q, json_file)
        return True
    
    def print_weights(self):
        for i in self.Q:
            print(i[0])
            print('-----------------------')
            c = 1
            for j in i[1]:
                c+=1
                print(*j, end = ' ')
                print('|', end = ' ')
                if c <= 3:
                    print(*i[c])
                else:
                    print()
            print()
#------------------------------------------------------------------------
class Reinforce:
    def __init__(self, size, agent, N, y = 0.9, url = ''):
        self.agent = agent
        self.N = N
        self.y = y
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.color = ''
        self.J = []
        self.score = []
        self.t = []
        self.epz = 0
        self.url = url

    def add_trajectory(self):
        R = 0
        for i in range(1, len(self.t)//3):
            R += self.y ** (i) * self.t[3*i]
        self.J.append([])
        self.J[-1].append(R)
        self.J[-1].append(self.t[0])
        for i in range(len(self.t[1:]) // 3):
            self.J[-1].append([])
            for j in self.t[1 + i * 3]:
                self.J[-1][-1].append(j.copy())
            self.J[-1].append(self.t[2 + i * 3])
            self.J[-1].append(self.t[3 + i * 3])

    def prov(self):
        for i in self.J:
            if i[1:] == self.t:
                return False
        return True
        
    def reward(self, score): # Вознаграждение
        if len(self.score) == 0:
            r = 0
            self.score = score
        else:
            r = score[0] - self.score[0] + self.score[1] - score[1]
            self.score = score
        return r
    
    def reform(self, board, act, score): # Преобразование доски, и списка для использования в матрице
        self.t.append([])
        for i in board:
            self.t[-1].append(i.copy())
        self.t.append(act)
        self.t.append(self.reward(score))
    
    def chose_action(self, board, slov, score, c = 0):
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        self.reform(board, pawn + move, score)
        return (pawn, move)

    def game(self, n):
        game = Environment(self.size)
        player = Players(game, self.url)
        if self.agent == 'usefulness':
            agent = player.usefulness_agent
        elif self.agent == 'greedy':
            agent = player.agent_greedy
        else:
            agent = player.agent_rand
        if n % 2 == 0:
            self.color = 'BK'
            self.t.append(self.color)
            (board, score, color) = game.env(agent, self.chose_action)
        else:
            self.color = 'WC'
            self.t.append(self.color)
            (board, score, color) = game.env(self.chose_action, agent)
        if color != self.color:
            m = score[1]
            score[1] = score[0]
            score[0] = m
        self.reform(board, '5252', score)
        if self.prov():
            self.add_trajectory()
        self.score = []
        self.t = []

    def lerning(self, progress = False, agent = 'null', N = 'null', y = 'null'):
        if agent != 'null': self.agent = agent
        if N != 'null': self.N = N
        if y != 'null': self.y = y
        for i in range(self.N):
            if progress:
                print('Прогресс: ' + str(int(((self.N - i) / self.N)*100)) + '%')
            self.game(i)

    def play(self, board, slov, score, c = 0):
        prov = float('-inf')
        inx = -1
        m = 0
        for i in self.J:
            if (len(i) - 2) / 3 > self.epz:
                if (i[2 + 3 * self.epz] == board) and (prov < i[0]) and (self.color == i[1]):
                    inx = m
                    prov = i[0]
            m+=1
        self.epz += 1
        if inx == -1:
            return self.chose_action(board, slov, score)
        else:
            return (self.J[inx][3 + 3 * (self.epz - 1)][:2], self.J[inx][3 + 3 * (self.epz - 1)][2:])
            
    def win_rate(self, N, agent):
        count = 0
        win = 0
        for n in range(N):
            self.epz = 0
            game = Environment(self.size)
            player = Players(game, self.url)
            if self.agent == 'usefulness':
                agent = player.usefulness_agent
            elif self.agent == 'greedy':
                agent = player.agent_greedy
            else:
                agent = player.agent_rand
            if n % 2 == 0:
                self.color = 'BK'
                (board, score, color) = game.env(agent, self.play)
            else:
                self.color = 'WC'
                (board, score, color) = game.env(self.play, agent)
            if self.color == color:
                win+=1
            count+=1
        self.t = []
        return round(win/count, 2)

    def save(self, file):
        if file[-5:] != '.json':
            return False
        with open(file, 'w') as json_file:
            json.dump(self.J, json_file)
        return True
    
    def print_weights(self):
        for i in self.J:
            print(i[0], i[1])
            print('-----------------------')
            for h in range(self.size + 1):
                print('|', end = ' ')
                for j in range(len(i[2:])//3):
                    if h < self.size:
                        print(*i[2+3*j][h], end = ' ')
                        print('|', end = ' ')
                    else:
                        m = 1 if i[4+3*j] == -1 else 0
                        print(str(i[3+3*j]) + ' ' * (self.size - m - 2) + str(i[4+3*j]), end = ' ')
                        print('|', end = ' ')
                print()
            print('-----------------------')
            print()
#------------------------------------------------------------------------
class Double_Qlerning:
    def __init__(self, size, agent, N, a = 0.1, y = 0.9, url = ''):
        self.agent = agent
        self.N = N
        self.n = True
        self.a = a
        self.y = y
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.eps = 1.0
        self.Q1 = []
        self.Q2 = []
        self.color = ''
        self.score = []
        self.inf = []
        self.play = False
        self.url = url
        
    def update_weight(self, inf, r): # Обновляет веса (Double Q-lerning)
        def search(Q1, Q2, inx):
            for i in Q2:
                if i == Q1:
                    try:
                        return i[3][inx]
                    except:
                        print(i, inx)
                        exit(52)
            return 0
        Q1 = self.Q1 if self.n else self.Q2
        Q2 = self.Q1 if not self.n else self.Q2
        Q1[inf[0]][3][inf[1]] += self.a * (r + self.y * search(Q1[inf[2]], Q2, Q1[inf[2]][3].index(max(Q1[inf[2]][3]))) - Q1[inf[0]][3][inf[1]])

    def prov(self, q): #Проверка наличия состояния в матрице и добавление если нет
        Q = self.Q1 if self.n else self.Q2
        for i in range(len(Q)):
            if Q[i][:3] == q[:3]:
                return i
        if not self.play:
            Q.append([])
            Q[-1].append(q[0])
            Q[-1].append([])
            for i in q[1]:
                Q[-1][1].append(i.copy())
            Q[-1].append(q[2].copy())
            Q[-1].append(q[3].copy())
            return len(Q) - 1
        else:
            return -1
            
    def reform(self, board, slov): # Преобразование доски, и списка для использования в матрице
        new_slov = []
        prikol = []
        for i in slov:
            for j in slov[i]:
                new_slov.append(i+j)
                prikol.append(0.0)
        return [self.color, board, new_slov, prikol]

    def reward(self, score): # Вознаграждение
        if len(self.score) == 0:
            r = 0
            self.score = score
        else:
            r = score[0] - self.score[0] + self.score[1] - score[1]
            self.score = score
        return r
    
    def rand(self, board, slov, q):
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        self.inf.append(q[2].index(pawn + move))
        return (pawn, move)

    def greedy(self, board, slov, q):
        Q = self.Q1 if self.n else self.Q2
        weigth = {}
        for i in slov:
            count = 0
            z = []
            for j in range(len(Q[self.inf[0]][2])):
                if Q[self.inf[0]][2][j][:2] == i:
                    count+=1
                    z.append(Q[self.inf[0]][3][j])
                if count == len(slov[i]):
                    break
            weigth.update({i:z})
        best = {}
        t = str(slov.keys())
        keys = t[12:len(t)-3].split("', '")
        mx = float('-inf')
        for i in keys:
            boy = False
            for j in range(len(slov[i])):
                if weigth[i][j] > mx:
                    best = {i:[slov[i][j]]}
                    mx = weigth[i][j]
                    boy = True
                elif weigth[i][j] == mx and boy:
                    best[i].append(slov[i][j])
                elif weigth[i][j] == mx and not boy:
                    best.update({i:[slov[i][j]]})
        return self.rand(board, best, q)
                
    def chose_action(self, board, slov, score, c = 0): # Выбор действия (рандомно или по умному)
        q = self.reform(board, slov)
        if not self.play:
            self.inf.append(self.prov(q))
            r = self.reward(score)
            if len(self.inf) > 2:
                self.update_weight(self.inf, r)
                for i in range(2):
                    self.inf.pop(0)
            rand = random.random()
            if rand <= self.eps:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
        else:
            self.inf = [self.prov(q)]
            if self.inf[0] == -1:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
            
    
    def game(self, n):
        game = Environment(self.size)
        player = Players(game, self.url)
        if self.agent == 'usefulness':
            agent = player.usefulness_agent
        elif self.agent == 'greedy':
            agent = player.agent_greedy
        else:
            agent = player.agent_rand
        if n % 2 == 0:
            self.color = 'BK'
            (board, score, color) = game.env(agent, self.chose_action)
        else:
            self.color = 'WC'
            (board, score, color) = game.env(self.chose_action, agent)
        if color != self.color:
            m = score[1]
            score[1] = score[0]
            score[0] = m
        slov = {'52': ['52']}
        q = self.reform(board, slov)
        self.inf.append(self.prov(q))
        self.update_weight(self.inf, self.reward(score))
        self.eps -= 1.0 / self.N
        self.score = []
        self.inf = []

    def lerning(self, progress = False, agent = 'null', N = 'null', a = 'null', y = 'null', eps = 'null'):
        if agent != 'null': self.agent = agent
        if eps != 'null': self.eps = eps
        if N != 'null': self.N = N
        if a != 'null': self.a = a
        if y != 'null': self.y = y
        lasteps = self.eps
        for n in range(self.N):
            if lasteps - self.eps > 0.01 and progress:
                lasteps -= 0.01
                print('Прогресс: ' + str(int((1 - lasteps)*100)) + '%')
            self.n = True if n % 4 < 2 else False
            self.game(n)

    def win_rate(self, N, agent):
        count = 0
        win = 0
        self.play = True
        self.n = True
        for n in range(N):
            game = Environment(self.size)
            player = Players(game, self.url)
            if self.agent == 'usefulness':
                agent = player.usefulness_agent
            elif self.agent == 'greedy':
                agent = player.agent_greedy
            else:
                agent = player.agent_rand
            if n % 2 == 0:
                self.color = 'BK'
                (board, score, color) = game.env(agent, self.chose_action)
            else:
                self.color = 'WC'
                (board, score, color) = game.env(self.chose_action, agent)
            if self.color == color:
                win+=1
            count+=1
        self.play = False
        self.inf = []
        return round(win/count, 2)

    def save(self, file):
        if file[-5:] != '.json':
            return False
        with open(file, 'w') as json_file:
            json.dump(self.Q1, json_file)
        return True
    
    def print_weights(self, z = True):
        Q = self.Q1 if z else self.Q2
        for i in Q:
            print(i[0])
            print('-----------------------')
            c = 1
            for j in i[1]:
                c+=1
                print(*j, end = ' ')
                print('|', end = ' ')
                if c <= 3:
                    print(*i[c])
                else:
                    print()
            print()
#------------------------------------------------------------------------
class Deferred_Qlerning:
    def __init__(self, size, agent, N, m = 5, a = 0.1, y = 0.9, url = ''):
        self.agent = agent
        self.N = N
        self.a = a
        self.y = y
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.eps = 1.0
        self.Q = []
        self.m = m
        self.n = []
        self.color = ''
        self.score = []
        self.inf = []
        self.play = False
        self.url = url
        
    def update_weight(self, inf, r): # Обновляет веса (Deferred Q-lerning)
        self.n[inf[0]][0][inf[1]] += 1
        if self.n[inf[0]][0][inf[1]] >= self.m:
            self.Q[inf[0]][3][inf[1]] += self.a * (self.n[inf[0]][1][inf[1]] + self.y * max(self.Q[inf[2]][3]) - self.Q[inf[0]][3][inf[1]])
        else:
            self.n[inf[0]][1][inf[1]] = r

    def prov(self, q): #Проверка наличия состояния в матрице и добавление если нет
        for i in range(len(self.Q)):
            if self.Q[i][:3] == q[:3]:
                return i
        if not self.play:
            self.n.append([])
            for i in range(2):
                self.n[-1].append([0] * len(q[3]))
            self.Q.append([])
            self.Q[-1].append(q[0])
            self.Q[-1].append([])
            for i in q[1]:
                self.Q[-1][1].append(i.copy())
            self.Q[-1].append(q[2].copy())
            self.Q[-1].append(q[3].copy())
            return len(self.Q) - 1
        else:
            return -1
            
    def reform(self, board, slov): # Преобразование доски, и списка для использования в матрице
        new_slov = []
        prikol = []
        for i in slov:
            for j in slov[i]:
                new_slov.append(i+j)
                prikol.append(0.0)
        return [self.color, board, new_slov, prikol]

    def reward(self, score): # Вознаграждение
        if len(self.score) == 0:
            r = 0
            self.score = score
        else:
            r = score[0] - self.score[0] + self.score[1] - score[1]
            self.score = score
        return r
    
    def rand(self, board, slov, q):
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        self.inf.append(q[2].index(pawn + move))
        return (pawn, move)

    def greedy(self, board, slov, q):
        weigth = {}
        for i in slov:
            count = 0
            z = []
            for j in range(len(self.Q[self.inf[0]][2])):
                if self.Q[self.inf[0]][2][j][:2] == i:
                    count+=1
                    z.append(self.Q[self.inf[0]][3][j])
                if count == len(slov[i]):
                    break
            weigth.update({i:z})
        best = {}
        t = str(slov.keys())
        keys = t[12:len(t)-3].split("', '")
        mx = float('-inf')
        for i in keys:
            boy = False
            for j in range(len(slov[i])):
                if weigth[i][j] > mx:
                    best = {i:[slov[i][j]]}
                    mx = weigth[i][j]
                    boy = True
                elif weigth[i][j] == mx and boy:
                    best[i].append(slov[i][j])
                elif weigth[i][j] == mx and not boy:
                    best.update({i:[slov[i][j]]})
        return self.rand(board, best, q)
                
    def chose_action(self, board, slov, score, c = 0): # Выбор действия (рандомно или по умному)
        q = self.reform(board, slov)
        if not self.play:
            self.inf.append(self.prov(q))
            r = self.reward(score)
            if len(self.inf) > 2:
                self.update_weight(self.inf, r)
                for i in range(2):
                    self.inf.pop(0)
            rand = random.random()
            if rand <= self.eps:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
        else:
            self.inf = [self.prov(q)]
            if self.inf[0] == -1:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
            
    
    def game(self, n):
        game = Environment(self.size)
        player = Players(game, self.url)
        if self.agent == 'usefulness':
            agent = player.usefulness_agent
        elif self.agent == 'greedy':
            agent = player.agent_greedy
        else:
            agent = player.agent_rand
        if n % 2 == 0:
            self.color = 'BK'
            (board, score, color) = game.env(agent, self.chose_action)
        else:
            self.color = 'WC'
            (board, score, color) = game.env(self.chose_action, agent)
        if color != self.color:
            m = score[1]
            score[1] = score[0]
            score[0] = m
        slov = {'52': ['52']}
        q = self.reform(board, slov)
        self.inf.append(self.prov(q))
        self.update_weight(self.inf, self.reward(score))
        self.eps -= 1.0 / self.N
        self.score = []
        self.inf = []

    def lerning(self, progress = False, agent = 'null', N = 'null', m = 'null', a = 'null', y = 'null', eps = 'null'):
        if agent != 'null': self.agent = agent
        if eps != 'null': self.eps = eps
        if N != 'null': self.N = N
        if m != 'null': self.m = m
        if a != 'null': self.a = a
        if y != 'null': self.y = y
        lasteps = self.eps
        for i in range(self.N):
            if lasteps - self.eps > 0.01 and progress:
                lasteps -= 0.01
                print('Прогресс: ' + str(int((1 - lasteps)*100)) + '%')
            self.game(i)

    def win_rate(self, N, agent):
        count = 0
        win = 0
        self.play = True
        for n in range(N):
            game = Environment(self.size)
            player = Players(game, self.url)
            if self.agent == 'usefulness':
                agent = player.usefulness_agent
            elif self.agent == 'greedy':
                agent = player.agent_greedy
            else:
                agent = player.agent_rand
            if n % 2 == 0:
                self.color = 'BK'
                (board, score, color) = game.env(agent, self.chose_action)
            else:
                self.color = 'WC'
                (board, score, color) = game.env(self.chose_action, agent)
            if self.color == color:
                win+=1
            count+=1
        self.play = False
        self.inf = []
        return round(win/count, 2)

    def save(self, file):
        if file[-5:] != '.json':
            return False
        with open(file, 'w') as json_file:
            json.dump(self.Q, json_file)
        return True
    
    def print_weights(self):
        for i in self.Q:
            print(i[0])
            print('-----------------------')
            c = 1
            for j in i[1]:
                c+=1
                print(*j, end = ' ')
                print('|', end = ' ')
                if c <= 3:
                    print(*i[c])
                else:
                    print()
            print()
#------------------------------------------------------------------------
class Opposition_Qlerning:
    def __init__(self, size, agent, N, p = 0.1, a = 0.1, y = 0.9, url = ''):
        self.agent = agent
        self.N = N
        self.a = a
        self.y = y
        self.p = p
        self.o = True
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.eps = 1.0
        self.Q = []
        self.color = ''
        self.score = []
        self.inf = []
        self.play = False
        self.url = url
        
    def update_weight(self, inf, r): # Обновляет веса (Opposition Q-lerning)
        self.Q[inf[0]][3][inf[1]] += self.a * (r + self.y * max(self.Q[inf[2]][3]) - self.Q[inf[0]][3][inf[1]])

    def prov(self, q): #Проверка наличия состояния в матрице и добавление если нет
        for i in range(len(self.Q)):
            if self.Q[i][:3] == q[:3]:
                return i
        if not self.play:
            self.Q.append([])
            self.Q[-1].append(q[0])
            self.Q[-1].append([])
            for i in q[1]:
                self.Q[-1][1].append(i.copy())
            self.Q[-1].append(q[2].copy())
            self.Q[-1].append(q[3].copy())
            return len(self.Q) - 1
        else:
            return -1
            
    def reform(self, board, slov): # Преобразование доски, и списка для использования в матрице
        new_slov = []
        prikol = []
        for i in slov:
            for j in slov[i]:
                new_slov.append(i+j)
                prikol.append(0.0)
        return [self.color, board, new_slov, prikol]

    def reward(self, score): # Вознаграждение
        if len(self.score) == 0:
            r = 0
            self.score = score
        else:
            r = score[0] - self.score[0] + self.score[1] - score[1]
            self.score = score
        return r
    
    def rand(self, board, slov, q):
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        self.inf.append(q[2].index(pawn + move))
        return (pawn, move)

    def greedy(self, board, slov, q):
        weigth = {}
        for i in slov:
            count = 0
            z = []
            for j in range(len(self.Q[self.inf[0]][2])):
                if self.Q[self.inf[0]][2][j][:2] == i:
                    count+=1
                    z.append(self.Q[self.inf[0]][3][j])
                if count == len(slov[i]):
                    break
            weigth.update({i:z})
        best = {}
        t = str(slov.keys())
        keys = t[12:len(t)-3].split("', '")
        mx = float('-inf') if self.o else float('+inf')
        for i in keys:
            boy = False
            for j in range(len(slov[i])):
                zov = weigth[i][j] >= mx if self.o else weigth[i][j] < mx
                if zov:
                    best = {i:[slov[i][j]]}
                    mx = weigth[i][j]
                    boy = True
                elif weigth[i][j] == mx and boy:
                    best[i].append(slov[i][j])
                elif weigth[i][j] == mx and not boy:
                    best.update({i:[slov[i][j]]})
        return self.rand(board, best, q)
                
    def chose_action(self, board, slov, score, c = 0): # Выбор действия (рандомно или по умному)
        q = self.reform(board, slov)
        if not self.play:
            self.inf.append(self.prov(q))
            r = self.reward(score)
            if len(self.inf) > 2:
                self.update_weight(self.inf, r)
                for i in range(2):
                    self.inf.pop(0)
            rand = random.random()
            if rand <= self.eps:
                return self.rand(board, slov, q)
            else:
                self.o = True if self.p < random.random() else False
                return self.greedy(board, slov, q)
        else:
            self.inf = [self.prov(q)]
            if self.inf[0] == -1:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
            
    
    def game(self, n):
        game = Environment(self.size)
        player = Players(game, self.url)
        if self.agent == 'usefulness':
            agent = player.usefulness_agent
        elif self.agent == 'greedy':
            agent = player.agent_greedy
        else:
            agent = player.agent_rand
        if n % 2 == 0:
            self.color = 'BK'
            (board, score, color) = game.env(agent, self.chose_action)
        else:
            self.color = 'WC'
            (board, score, color) = game.env(self.chose_action, agent)
        if color != self.color:
            m = score[1]
            score[1] = score[0]
            score[0] = m
        slov = {'52': ['52']}
        q = self.reform(board, slov)
        self.inf.append(self.prov(q))
        self.update_weight(self.inf, self.reward(score))
        self.eps -= 1.0 / self.N
        self.score = []
        self.inf = []

    def lerning(self, progress = False, agent = 'null', N = 'null', p = 'null', a = 'null', y = 'null', eps = 'null'):
        if agent != 'null': self.agent = agent
        if eps != 'null': self.eps = eps
        if N != 'null': self.N = N
        if p != 'null': self.p = p
        if a != 'null': self.a = a
        if y != 'null': self.y = y
        lasteps = self.eps
        for i in range(self.N):
            if lasteps - self.eps > 0.01 and progress:
                lasteps -= 0.01
                print('Прогресс: ' + str(int((1 - lasteps)*100)) + '%')
            self.game(i)

    def win_rate(self, N, agent):
        count = 0
        win = 0
        self.play = True
        for n in range(N):
            game = Environment(self.size)
            player = Players(game, self.url)
            if self.agent == 'usefulness':
                agent = player.usefulness_agent
            elif self.agent == 'greedy':
                agent = player.agent_greedy
            else:
                agent = player.agent_rand
            if n % 2 == 0:
                self.color = 'BK'
                (board, score, color) = game.env(agent, self.chose_action)
            else:
                self.color = 'WC'
                (board, score, color) = game.env(self.chose_action, agent)
            if self.color == color:
                win+=1
            count+=1
        self.play = False
        self.inf = []
        return round(win/count, 2)

    def save(self, file):
        if file[-5:] != '.json':
            return False
        with open(file, 'w') as json_file:
            json.dump(self.Q, json_file)
        return True
    
    def print_weights(self):
        for i in self.Q:
            print(i[0])
            print('-----------------------')
            c = 1
            for j in i[1]:
                c+=1
                print(*j, end = ' ')
                print('|', end = ' ')
                if c <= 3:
                    print(*i[c])
                else:
                    print()
            print()
#------------------------------------------------------------------------
class Nstep_Qlerning:
    def __init__(self, size, agent, N, n = 2, a = 0.1, y = 0.9, url = ''):
        self.agent = agent
        self.N = N
        self.n = n
        self.a = a
        self.y = y
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.eps = 1.0
        self.Q = []
        self.G = [0] * n
        self.step = 0
        self.color = ''
        self.score = []
        self.inf = []
        self.arrinf = []
        self.play = False
        self.z = 0
        self.url = url
        
    def update_weight(self, inf, r): # Обновляет веса (n step Q-lerning)
        def izm(G, step, r, y):
            t = -1
            for i in range(1, len(G)):
                G[-i] = G[-i-1]
                t = -i - 1
            G[t] = 0
            for i in range(step):
                G[i] += r if i == 0 else (y ** i) * (r ** i)
        if self.step < self.n:
            self.step += 1
            self.arrinf.append(inf.copy())
        else:
            m = self.n + 2 if self.Q[inf[2]][2][0] == '5252' else 2
            self.arrinf.append(inf.copy())
            for i in range(1, m):
                inf = self.arrinf.pop(0)
                if i < len(self.G):
                    self.G[-i] += (self.y ** (self.n + 1 - i)) * max(self.Q[inf[2]][3])
                else:
                    self.G.append(r + self.y * max(self.Q[inf[2]][3]))
                self.Q[inf[0]][3][inf[1]] += self.a * (self.G[-1] - self.Q[inf[0]][3][inf[1]])
        izm(self.G, self.step, r, self.y)
            
    def prov(self, q): #Проверка наличия состояния в матрице и добавление если нет
        for i in range(len(self.Q)):
            if self.Q[i][:3] == q[:3]:
                return i
        if not self.play:
            self.Q.append([])
            self.Q[-1].append(q[0])
            self.Q[-1].append([])
            for i in q[1]:
                self.Q[-1][1].append(i.copy())
            self.Q[-1].append(q[2].copy())
            self.Q[-1].append(q[3].copy())
            return len(self.Q) - 1
        else:
            return -1
            
    def reform(self, board, slov): # Преобразование доски, и списка для использования в матрице
        new_slov = []
        prikol = []
        for i in slov:
            for j in slov[i]:
                new_slov.append(i+j)
                prikol.append(0.0)
        return [self.color, board, new_slov, prikol]

    def reward(self, score): # Вознаграждение
        if len(self.score) == 0:
            r = 0
            self.score = score
        else:
            r = score[0] - self.score[0] + self.score[1] - score[1]
            self.score = score
        return r
    
    def rand(self, board, slov, q):
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        self.inf.append(q[2].index(pawn + move))
        return (pawn, move)

    def greedy(self, board, slov, q):
        weigth = {}
        for i in slov:
            count = 0
            z = []
            for j in range(len(self.Q[self.inf[0]][2])):
                if self.Q[self.inf[0]][2][j][:2] == i:
                    count+=1
                    z.append(self.Q[self.inf[0]][3][j])
                if count == len(slov[i]):
                    break
            weigth.update({i:z})
        best = {}
        t = str(slov.keys())
        keys = t[12:len(t)-3].split("', '")
        mx = float('-inf')
        for i in keys:
            boy = False
            for j in range(len(slov[i])):
                if weigth[i][j] > mx:
                    best = {i:[slov[i][j]]}
                    mx = weigth[i][j]
                    boy = True
                elif weigth[i][j] == mx and boy:
                    best[i].append(slov[i][j])
                elif weigth[i][j] == mx and not boy:
                    best.update({i:[slov[i][j]]})
        return self.rand(board, best, q)
                
    def chose_action(self, board, slov, score, c = 0): # Выбор действия (рандомно или по умному)
        q = self.reform(board, slov)
        '''self.z += 1
        if self.z % 1000 == 999:
            print(board, self.score)'''
        if not self.play:
            self.inf.append(self.prov(q))
            r = self.reward(score)
            if len(self.inf) > 2:
                self.update_weight(self.inf, r)
                for i in range(2):
                    self.inf.pop(0)
            rand = random.random()
            if rand <= self.eps:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
        else:
            self.inf = [self.prov(q)]
            if self.inf[0] == -1:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
            
    
    def game(self, n):
        self.G = [0] * self.n
        self.step = 0
        self.arrinf = []
        game = Environment(self.size)
        player = Players(game, self.url)
        if self.agent == 'usefulness':
            agent = player.usefulness_agent
        elif self.agent == 'greedy':
            agent = player.agent_greedy
        else:
            agent = player.agent_rand
        if n % 2 == 0:
            self.color = 'BK'
            (board, score, color) = game.env(agent, self.chose_action)
        else:
            self.color = 'WC'
            (board, score, color) = game.env(self.chose_action, agent)
        if color != self.color:
            m = score[1]
            score[1] = score[0]
            score[0] = m
        slov = {'52': ['52']}
        q = self.reform(board, slov)
        self.inf.append(self.prov(q))
        self.update_weight(self.inf, self.reward(score))
        self.eps -= 1.0 / self.N
        self.score = []
        self.inf = []

    def lerning(self, progress = False, agent = 'null', N = 'null', n = 'null', a = 'null', y = 'null', eps = 'null'):
        if agent != 'null': self.agent = agent
        if eps != 'null': self.eps = eps
        if N != 'null': self.N = N
        if n != 'null': self.n = n
        if a != 'null': self.a = a
        if y != 'null': self.y = y
        lasteps = self.eps
        for i in range(self.N):
            if lasteps - self.eps > 0.01 and progress:
                lasteps -= 0.01
                print('Прогресс: ' + str(int((1 - lasteps)*100)) + '%')
            self.game(i)

    def win_rate(self, N, agent):
        count = 0
        win = 0
        self.play = True
        for n in range(N):
            game = Environment(self.size)
            player = Players(game, self.url)
            if self.agent == 'usefulness':
                agent = player.usefulness_agent
            elif self.agent == 'greedy':
                agent = player.agent_greedy
            else:
                agent = player.agent_rand
            if n % 2 == 0:
                self.color = 'BK'
                (board, score, color) = game.env(agent, self.chose_action)
            else:
                self.color = 'WC'
                (board, score, color) = game.env(self.chose_action, agent)
            if self.color == color:
                win+=1
            count+=1
        self.play = False
        self.inf = []
        return round(win/count, 2)

    def save(self, file):
        if file[-5:] != '.json':
            return False
        with open(file, 'w') as json_file:
            json.dump(self.Q, json_file)
        return True
    
    def print_weights(self):
        for i in self.Q:
            print(i[0])
            print('-----------------------')
            c = 1
            for j in i[1]:
                c+=1
                print(*j, end = ' ')
                print('|', end = ' ')
                if c <= 3:
                    print(*i[c])
                else:
                    print()
            print()
#------------------------------------------------------------------------
class Watkins_Qlerning:
    def __init__(self, size, agent, N, a = 0.1, y = 0.9, url = ''):
        self.agent = agent
        self.N = N
        self.a = a
        self.y = y
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.eps = 1.0
        self.Q = []
        self.color = ''
        self.score = []
        self.inf = []
        self.play = False
        self.url = url
        
    def update_weight(self, inf, r): # Обновляет веса (Q-lerning Уоткинса)
        mx = max(self.Q[inf[2]][3])
        if mx < 0:
            mx = 0
        self.Q[inf[0]][3][inf[1]] += self.a * (r + self.y * mx - self.Q[inf[0]][3][inf[1]])

    def prov(self, q): #Проверка наличия состояния в матрице и добавление если нет
        for i in range(len(self.Q)):
            if self.Q[i][:3] == q[:3]:
                return i
        if not self.play:
            self.Q.append([])
            self.Q[-1].append(q[0])
            self.Q[-1].append([])
            for i in q[1]:
                self.Q[-1][1].append(i.copy())
            self.Q[-1].append(q[2].copy())
            self.Q[-1].append(q[3].copy())
            return len(self.Q) - 1
        else:
            return -1
            
    def reform(self, board, slov): # Преобразование доски, и списка для использования в матрице
        new_slov = []
        prikol = []
        for i in slov:
            for j in slov[i]:
                new_slov.append(i+j)
                prikol.append(0.0)
        return [self.color, board, new_slov, prikol]

    def reward(self, score): # Вознаграждение
        if len(self.score) == 0:
            r = 0
            self.score = score
        else:
            r = score[0] - self.score[0] + self.score[1] - score[1]
            self.score = score
        return r
    
    def rand(self, board, slov, q):
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        self.inf.append(q[2].index(pawn + move))
        return (pawn, move)

    def greedy(self, board, slov, q):
        weigth = {}
        for i in slov:
            count = 0
            z = []
            for j in range(len(self.Q[self.inf[0]][2])):
                if self.Q[self.inf[0]][2][j][:2] == i:
                    count+=1
                    z.append(self.Q[self.inf[0]][3][j])
                if count == len(slov[i]):
                    break
            weigth.update({i:z})
        best = {}
        t = str(slov.keys())
        keys = t[12:len(t)-3].split("', '")
        mx = float('-inf')
        for i in keys:
            boy = False
            for j in range(len(slov[i])):
                if weigth[i][j] > mx:
                    best = {i:[slov[i][j]]}
                    mx = weigth[i][j]
                    boy = True
                elif weigth[i][j] == mx and boy:
                    best[i].append(slov[i][j])
                elif weigth[i][j] == mx and not boy:
                    best.update({i:[slov[i][j]]})
        return self.rand(board, best, q)
                
    def chose_action(self, board, slov, score, c = 0): # Выбор действия (рандомно или по умному)
        q = self.reform(board, slov)
        if not self.play:
            self.inf.append(self.prov(q))
            r = self.reward(score)
            if len(self.inf) > 2:
                self.update_weight(self.inf, r)
                for i in range(2):
                    self.inf.pop(0)
            rand = random.random()
            if rand <= self.eps:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
        else:
            self.inf = [self.prov(q)]
            if self.inf[0] == -1:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
            
    
    def game(self, n):
        game = Environment(self.size)
        player = Players(game, self.url)
        if self.agent == 'usefulness':
            agent = player.usefulness_agent
        elif self.agent == 'greedy':
            agent = player.agent_greedy
        else:
            agent = player.agent_rand
        if n % 2 == 0:
            self.color = 'BK'
            (board, score, color) = game.env(agent, self.chose_action)
        else:
            self.color = 'WC'
            (board, score, color) = game.env(self.chose_action, agent)
        if color != self.color:
            m = score[1]
            score[1] = score[0]
            score[0] = m
        slov = {'52': ['52']}
        q = self.reform(board, slov)
        self.inf.append(self.prov(q))
        self.update_weight(self.inf, self.reward(score))
        self.eps -= 1.0 / self.N
        self.score = []
        self.inf = []

    def lerning(self, progress = False, agent = 'null', N = 'null', a = 'null', y = 'null', eps = 'null'):
        if agent != 'null': self.agent = agent
        if eps != 'null': self.eps = eps
        if N != 'null': self.N = N
        if a != 'null': self.a = a
        if y != 'null': self.y = y
        lasteps = self.eps
        for i in range(self.N):
            if lasteps - self.eps > 0.01 and progress:
                lasteps -= 0.01
                print('Прогресс: ' + str(int((1 - lasteps)*100)) + '%')
            self.game(i)

    def win_rate(self, N, agent):
        count = 0
        win = 0
        self.play = True
        for n in range(N):
            game = Environment(self.size)
            player = Players(game, self.url)
            if self.agent == 'usefulness':
                agent = player.usefulness_agent
            elif self.agent == 'greedy':
                agent = player.agent_greedy
            else:
                agent = player.agent_rand
            if n % 2 == 0:
                self.color = 'BK'
                (board, score, color) = game.env(agent, self.chose_action)
            else:
                self.color = 'WC'
                (board, score, color) = game.env(self.chose_action, agent)
            if self.color == color:
                win+=1
            count+=1
        self.play = False
        self.inf = []
        return round(win/count, 2)

    def save(self, file):
        if file[-5:] != '.json':
            return False
        with open(file, 'w') as json_file:
            json.dump(self.Q, json_file)
        return True
    
    def print_weights(self):
        for i in self.Q:
            print(i[0])
            print('-----------------------')
            c = 1
            for j in i[1]:
                c+=1
                print(*j, end = ' ')
                print('|', end = ' ')
                if c <= 3:
                    print(*i[c])
                else:
                    print()
            print()
#------------------------------------------------------------------------
class FuzEras_Watkins_Qlerning:
    def __init__(self, size, agent, N, mstep = 5, a = 0.1, y = 0.9, url = ''):
        self.agent = agent
        self.N = N
        self.a = a
        self.y = y
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.eps = 1.0
        self.Q = []
        self.color = ''
        self.score = []
        self.inf = []
        self.play = False
        self.step = 0
        self.mstep = mstep
        self.url = url
        
    def update_weight(self, inf, r): # Обновляет веса (Q-lerning Уоткинса с нечеткими стираниями)
        mx = max(self.Q[inf[2]][3])
        self.step += 1
        if mx < 0 and self.step <= self.mstep:
            mx = 0
        self.Q[inf[0]][3][inf[1]] += self.a * (r + self.y * mx - self.Q[inf[0]][3][inf[1]])

    def prov(self, q): #Проверка наличия состояния в матрице и добавление если нет
        for i in range(len(self.Q)):
            if self.Q[i][:3] == q[:3]:
                return i
        if not self.play:
            self.Q.append([])
            self.Q[-1].append(q[0])
            self.Q[-1].append([])
            for i in q[1]:
                self.Q[-1][1].append(i.copy())
            self.Q[-1].append(q[2].copy())
            self.Q[-1].append(q[3].copy())
            return len(self.Q) - 1
        else:
            return -1
            
    def reform(self, board, slov): # Преобразование доски, и списка для использования в матрице
        new_slov = []
        prikol = []
        for i in slov:
            for j in slov[i]:
                new_slov.append(i+j)
                prikol.append(0.0)
        return [self.color, board, new_slov, prikol]

    def reward(self, score): # Вознаграждение
        if len(self.score) == 0:
            r = 0
            self.score = score
        else:
            r = score[0] - self.score[0] + self.score[1] - score[1]
            self.score = score
        return r
    
    def rand(self, board, slov, q):
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        self.inf.append(q[2].index(pawn + move))
        return (pawn, move)

    def greedy(self, board, slov, q):
        weigth = {}
        for i in slov:
            count = 0
            z = []
            for j in range(len(self.Q[self.inf[0]][2])):
                if self.Q[self.inf[0]][2][j][:2] == i:
                    count+=1
                    z.append(self.Q[self.inf[0]][3][j])
                if count == len(slov[i]):
                    break
            weigth.update({i:z})
        best = {}
        t = str(slov.keys())
        keys = t[12:len(t)-3].split("', '")
        mx = float('-inf')
        for i in keys:
            boy = False
            for j in range(len(slov[i])):
                if weigth[i][j] > mx:
                    best = {i:[slov[i][j]]}
                    mx = weigth[i][j]
                    boy = True
                elif weigth[i][j] == mx and boy:
                    best[i].append(slov[i][j])
                elif weigth[i][j] == mx and not boy:
                    best.update({i:[slov[i][j]]})
        return self.rand(board, best, q)
                
    def chose_action(self, board, slov, score, c = 0): # Выбор действия (рандомно или по умному)
        q = self.reform(board, slov)
        if not self.play:
            self.inf.append(self.prov(q))
            r = self.reward(score)
            if len(self.inf) > 2:
                self.update_weight(self.inf, r)
                for i in range(2):
                    self.inf.pop(0)
            rand = random.random()
            if rand <= self.eps:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
        else:
            self.inf = [self.prov(q)]
            if self.inf[0] == -1:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
            
    
    def game(self, n):
        self.step = 0
        game = Environment(self.size)
        player = Players(game, self.url)
        if self.agent == 'usefulness':
            agent = player.usefulness_agent
        elif self.agent == 'greedy':
            agent = player.agent_greedy
        else:
            agent = player.agent_rand
        if n % 2 == 0:
            self.color = 'BK'
            (board, score, color) = game.env(agent, self.chose_action)
        else:
            self.color = 'WC'
            (board, score, color) = game.env(self.chose_action, agent)
        if color != self.color:
            m = score[1]
            score[1] = score[0]
            score[0] = m
        slov = {'52': ['52']}
        q = self.reform(board, slov)
        self.inf.append(self.prov(q))
        self.update_weight(self.inf, self.reward(score))
        self.eps -= 1.0 / self.N
        self.score = []
        self.inf = []

    def lerning(self, progress = False, agent = 'null', N = 'null', mstep = 'null', a = 'null', y = 'null', eps = 'null'):
        if agent != 'null': self.agent = agent
        if eps != 'null': self.eps = eps
        if N != 'null': self.N = N
        if mstep != 'null': self.mstep = mstep
        if a != 'null': self.a = a
        if y != 'null': self.y = y
        lasteps = self.eps
        for i in range(self.N):
            if lasteps - self.eps > 0.01 and progress:
                lasteps -= 0.01
                print('Прогресс: ' + str(int((1 - lasteps)*100)) + '%')
            self.game(i)

    def win_rate(self, N, agent):
        count = 0
        win = 0
        self.play = True
        for n in range(N):
            game = Environment(self.size)
            player = Players(game, self.url)
            if self.agent == 'usefulness':
                agent = player.usefulness_agent
            elif self.agent == 'greedy':
                agent = player.agent_greedy
            else:
                agent = player.agent_rand
            if n % 2 == 0:
                self.color = 'BK'
                (board, score, color) = game.env(agent, self.chose_action)
            else:
                self.color = 'WC'
                (board, score, color) = game.env(self.chose_action, agent)
            if self.color == color:
                win+=1
            count+=1
        self.play = False
        self.inf = []
        return round(win/count, 2)

    def save(self, file):
        if file[-5:] != '.json':
            return False
        with open(file, 'w') as json_file:
            json.dump(self.Q, json_file)
        return True
    
    def print_weights(self):
        for i in self.Q:
            print(i[0])
            print('-----------------------')
            c = 1
            for j in i[1]:
                c+=1
                print(*j, end = ' ')
                print('|', end = ' ')
                if c <= 3:
                    print(*i[c])
                else:
                    print()
            print()
#------------------------------------------------------------------------
class Fast_Qlerning:
    def __init__(self, size, agent, N, a = 0.1, y = 0.9, url = ''):
        self.agent = agent
        self.N = N
        self.a = a
        self.y = y
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.eps = 1.0
        self.Q = []
        self.color = ''
        self.score = []
        self.inf = []
        self.play = False
        self.url = url
        
    def update_weight(self, inf, r): # Обновляет веса (Fast Q-lerning)
        mx = max(self.Q[inf[2]][3])
        n = 1 if r == 0 or mx == 0 else 2
        self.Q[inf[0]][3][inf[1]] += self.a / n * (r + self.y * mx - self.Q[inf[0]][3][inf[1]])

    def prov(self, q): #Проверка наличия состояния в матрице и добавление если нет
        for i in range(len(self.Q)):
            if self.Q[i][:3] == q[:3]:
                return i
        if not self.play:
            self.Q.append([])
            self.Q[-1].append(q[0])
            self.Q[-1].append([])
            for i in q[1]:
                self.Q[-1][1].append(i.copy())
            self.Q[-1].append(q[2].copy())
            self.Q[-1].append(q[3].copy())
            return len(self.Q) - 1
        else:
            return -1
            
    def reform(self, board, slov): # Преобразование доски, и списка для использования в матрице
        new_slov = []
        prikol = []
        for i in slov:
            for j in slov[i]:
                new_slov.append(i+j)
                prikol.append(0.0)
        return [self.color, board, new_slov, prikol]

    def reward(self, score): # Вознаграждение
        if len(self.score) == 0:
            r = 0
            self.score = score
        else:
            r = score[0] - self.score[0] + self.score[1] - score[1]
            self.score = score
        return r
    
    def rand(self, board, slov, q):
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        self.inf.append(q[2].index(pawn + move))
        return (pawn, move)

    def greedy(self, board, slov, q):
        weigth = {}
        for i in slov:
            count = 0
            z = []
            for j in range(len(self.Q[self.inf[0]][2])):
                if self.Q[self.inf[0]][2][j][:2] == i:
                    count+=1
                    z.append(self.Q[self.inf[0]][3][j])
                if count == len(slov[i]):
                    break
            weigth.update({i:z})
        best = {}
        t = str(slov.keys())
        keys = t[12:len(t)-3].split("', '")
        mx = float('-inf')
        for i in keys:
            boy = False
            for j in range(len(slov[i])):
                if weigth[i][j] > mx:
                    best = {i:[slov[i][j]]}
                    mx = weigth[i][j]
                    boy = True
                elif weigth[i][j] == mx and boy:
                    best[i].append(slov[i][j])
                elif weigth[i][j] == mx and not boy:
                    best.update({i:[slov[i][j]]})
        return self.rand(board, best, q)
                
    def chose_action(self, board, slov, score, c = 0): # Выбор действия (рандомно или по умному)
        q = self.reform(board, slov)
        if not self.play:
            self.inf.append(self.prov(q))
            r = self.reward(score)
            if len(self.inf) > 2:
                self.update_weight(self.inf, r)
                for i in range(2):
                    self.inf.pop(0)
            rand = random.random()
            if rand <= self.eps:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
        else:
            self.inf = [self.prov(q)]
            if self.inf[0] == -1:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
            
    
    def game(self, n):
        game = Environment(self.size)
        player = Players(game, self.url)
        if self.agent == 'usefulness':
            agent = player.usefulness_agent
        elif self.agent == 'greedy':
            agent = player.agent_greedy
        else:
            agent = player.agent_rand
        if n % 2 == 0:
            self.color = 'BK'
            (board, score, color) = game.env(agent, self.chose_action)
        else:
            self.color = 'WC'
            (board, score, color) = game.env(self.chose_action, agent)
        if color != self.color:
            m = score[1]
            score[1] = score[0]
            score[0] = m
        slov = {'52': ['52']}
        q = self.reform(board, slov)
        self.inf.append(self.prov(q))
        self.update_weight(self.inf, self.reward(score))
        self.eps -= 1.0 / self.N
        self.score = []
        self.inf = []

    def lerning(self, progress = False, agent = 'null', N = 'null', a = 'null', y = 'null', eps = 'null'):
        if agent != 'null': self.agent = agent
        if eps != 'null': self.eps = eps
        if N != 'null': self.N = N
        if a != 'null': self.a = a
        if y != 'null': self.y = y
        lasteps = self.eps
        for i in range(self.N):
            if lasteps - self.eps > 0.01 and progress:
                lasteps -= 0.01
                print('Прогресс: ' + str(int((1 - lasteps)*100)) + '%')
            self.game(i)

    def win_rate(self, N, agent):
        count = 0
        win = 0
        self.play = True
        for n in range(N):
            game = Environment(self.size)
            player = Players(game, self.url)
            if self.agent == 'usefulness':
                agent = player.usefulness_agent
            elif self.agent == 'greedy':
                agent = player.agent_greedy
            else:
                agent = player.agent_rand
            if n % 2 == 0:
                self.color = 'BK'
                (board, score, color) = game.env(agent, self.chose_action)
            else:
                self.color = 'WC'
                (board, score, color) = game.env(self.chose_action, agent)
            if self.color == color:
                win+=1
            count+=1
        self.play = False
        self.inf = []
        return round(win/count, 2)

    def save(self, file):
        if file[-5:] != '.json':
            return False
        with open(file, 'w') as json_file:
            json.dump(self.Q, json_file)
        return True
    
    def print_weights(self):
        for i in self.Q:
            print(i[0])
            print('-----------------------')
            c = 1
            for j in i[1]:
                c+=1
                print(*j, end = ' ')
                print('|', end = ' ')
                if c <= 3:
                    print(*i[c])
                else:
                    print()
            print()
#------------------------------------------------------------------------
class Storage_Qlerning:
    def __init__(self, size, agent, N, a = 0.1, y = 0.9, url = ''):
        self.agent = agent
        self.N = N
        self.a = a
        self.y = y
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.eps = 1.0
        self.Q = []
        self.n = []
        self.color = ''
        self.score = []
        self.inf = []
        self.play = False
        self.url = url
        
    def update_weight(self, inf, r): # Обновляет веса (Накопление трасировок соответствия Q-lerning)
        self.n[inf[0]][inf[1]] += 1
        self.Q[inf[0]][3][inf[1]] += (3 - (self.n[inf[0]][inf[1]] + 1) / (self.n[inf[0]][inf[1]])) * self.a * (r + self.y * max(self.Q[inf[2]][3]) - self.Q[inf[0]][3][inf[1]])

    def prov(self, q): #Проверка наличия состояния в матрице и добавление если нет
        for i in range(len(self.Q)):
            if self.Q[i][:3] == q[:3]:
                return i
        if not self.play:
            self.n.append(q[3].copy())
            self.Q.append([])
            self.Q[-1].append(q[0])
            self.Q[-1].append([])
            for i in q[1]:
                self.Q[-1][1].append(i.copy())
            self.Q[-1].append(q[2].copy())
            self.Q[-1].append(q[3].copy())
            return len(self.Q) - 1
        else:
            return -1
            
    def reform(self, board, slov): # Преобразование доски, и списка для использования в матрице
        new_slov = []
        prikol = []
        for i in slov:
            for j in slov[i]:
                new_slov.append(i+j)
                prikol.append(0.0)
        return [self.color, board, new_slov, prikol]

    def reward(self, score): # Вознаграждение
        if len(self.score) == 0:
            r = 0
            self.score = score
        else:
            r = score[0] - self.score[0] + self.score[1] - score[1]
            self.score = score
        return r
    
    def rand(self, board, slov, q):
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        self.inf.append(q[2].index(pawn + move))
        return (pawn, move)

    def greedy(self, board, slov, q):
        weigth = {}
        for i in slov:
            count = 0
            z = []
            for j in range(len(self.Q[self.inf[0]][2])):
                if self.Q[self.inf[0]][2][j][:2] == i:
                    count+=1
                    z.append(self.Q[self.inf[0]][3][j])
                if count == len(slov[i]):
                    break
            weigth.update({i:z})
        best = {}
        t = str(slov.keys())
        keys = t[12:len(t)-3].split("', '")
        mx = float('-inf')
        for i in keys:
            boy = False
            for j in range(len(slov[i])):
                if weigth[i][j] > mx:
                    best = {i:[slov[i][j]]}
                    mx = weigth[i][j]
                    boy = True
                elif weigth[i][j] == mx and boy:
                    best[i].append(slov[i][j])
                elif weigth[i][j] == mx and not boy:
                    best.update({i:[slov[i][j]]})
        return self.rand(board, best, q)
                
    def chose_action(self, board, slov, score, c = 0): # Выбор действия (рандомно или по умному)
        q = self.reform(board, slov)
        if not self.play:
            self.inf.append(self.prov(q))
            r = self.reward(score)
            if len(self.inf) > 2:
                self.update_weight(self.inf, r)
                for i in range(2):
                    self.inf.pop(0)
            rand = random.random()
            if rand <= self.eps:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
        else:
            self.inf = [self.prov(q)]
            if self.inf[0] == -1:
                return self.rand(board, slov, q)
            else:
                return self.greedy(board, slov, q)
            
    
    def game(self, n):
        game = Environment(self.size)
        player = Players(game, self.url)
        if self.agent == 'usefulness':
            agent = player.usefulness_agent
        elif self.agent == 'greedy':
            agent = player.agent_greedy
        else:
            agent = player.agent_rand
        if n % 2 == 0:
            self.color = 'BK'
            (board, score, color) = game.env(agent, self.chose_action)
        else:
            self.color = 'WC'
            (board, score, color) = game.env(self.chose_action, agent)
        if color != self.color:
            m = score[1]
            score[1] = score[0]
            score[0] = m
        slov = {'52': ['52']}
        q = self.reform(board, slov)
        self.inf.append(self.prov(q))
        self.update_weight(self.inf, self.reward(score))
        self.eps -= 1.0 / self.N
        self.score = []
        self.inf = []

    def lerning(self, progress = False, agent = 'null', N = 'null', a = 'null', y = 'null', eps = 'null'):
        if agent != 'null': self.agent = agent
        if eps != 'null': self.eps = eps
        if N != 'null': self.N = N
        if a != 'null': self.a = a
        if y != 'null': self.y = y
        lasteps = self.eps
        for i in range(self.N):
            if lasteps - self.eps > 0.01 and progress:
                lasteps -= 0.01
                print('Прогресс: ' + str(int((1 - lasteps)*100)) + '%')
            self.game(i)

    def win_rate(self, N, agent):
        count = 0
        win = 0
        self.play = True
        for n in range(N):
            game = Environment(self.size)
            player = Players(game, self.url)
            if self.agent == 'usefulness':
                agent = player.usefulness_agent
            elif self.agent == 'greedy':
                agent = player.agent_greedy
            else:
                agent = player.agent_rand
            if n % 2 == 0:
                self.color = 'BK'
                (board, score, color) = game.env(agent, self.chose_action)
            else:
                self.color = 'WC'
                (board, score, color) = game.env(self.chose_action, agent)
            if self.color == color:
                win+=1
            count+=1
        self.play = False
        self.inf = []
        return round(win/count, 2)

    def save(self, file):
        if file[-5:] != '.json':
            return False
        with open(file, 'w') as json_file:
            json.dump(self.Q, json_file)
        return True
    
    def print_weights(self):
        for i in self.Q:
            print(i[0])
            print('-----------------------')
            c = 1
            for j in i[1]:
                c+=1
                print(*j, end = ' ')
                print('|', end = ' ')
                if c <= 3:
                    print(*i[c])
                else:
                    print()
            print()
#------------------------------------------------------------------------
z = [4,20000]
'''print('qlerning')
model = Qlerning(z[0], 'rand', z[1], 0.5)
model.lerning(False, agent = 'rand')
print(model.win_rate(100, 'rand'))
print(model.win_rate(100, 'rand'))
print(model.win_rate(100, 'rand'))
model.save('Agents//qlerning'+ str(z[0]) + '.json')
del model
print('nstepqlerning')
model = Nstep_Qlerning(z[0], 'rand', z[1], 5, 0.5)
model.lerning(False, agent = 'rand')
print(model.win_rate(100, 'rand'))
print(model.win_rate(100, 'rand'))
print(model.win_rate(100, 'rand'))
model.save('Agents//nstepqlerning'+ str(z[0])+ '.json')'''
