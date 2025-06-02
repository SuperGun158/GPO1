import random
import json
import pygame
from PIL import Image, ImageDraw

class Environment:
    def __init__(self, size = 8, maximg = 20, lim = -1):
        self.size = 4 if size - size % 2 <= 4 else size - size % 2
        self.black = 0
        self.white = 0
        self.step = 0
        self.mxstep = maximg
        self.zov = True
        self.lim = lim
    def board(self):
        board = []
        for i in range(self.size):
            board.append(['S'] * self.size)
        for i in range(self.size - 2):
            z = (1+i)%2
            m = (self.size - 2) // 2 
            for j in range(z, m + 1 + z):
                n = 'W' if i - m >= 0 else 'B'
                board[i-m][j*2-z] = n
        return board

    def prov(self, sign, i, j, board, colors, slov, size, m = True):
        z = []
        for t in (sign*(-1), sign):
            if (i + sign >= 0 and i + sign <= size - 1) and (j + t*sign >= 0 and j + t*sign <= size - 1):
                if board[i + sign][j + t*sign] == 'S':
                    if m and self.zov:
                        z.append(str(i + sign) + str(j + t*sign))
        for t in (sign*(-1), sign):
            for g in (-1,1):
                if (i + g*sign*2 >= 0 and i + g*sign*2 <= size - 1) and (j + t*sign*2 >= 0 and j + t*sign*2 <= size - 1):
                    if not (board[i + g*sign][j + t*sign] in 'S' + colors):
                        if (i + g*sign*2 >= 0 and i + g*sign*2 <= size - 1) and (j + t*sign*2 >= 0 and j + t*sign*2 <= size - 1):
                            if board[i + g*sign*2][j + t*sign*2] == 'S':
                                if self.zov:
                                    self.zov = False
                                    z = []
                                    slov.clear()
                                z.append(str(i + g*sign*2) + str(j + t*sign*2))
        if len(z) > 0:
            slov.update({str(i) + str(j): z})
            
    def provKing(self, i, j, board, colors, slov, size, m = True):
        z = []
        for n in (-1, 1):
            for g in (-1, 1):
                a = i + n
                b = j + g
                c = 0
                boy = False
                while(a <= size - 1 and a >= 0 and b <= size - 1 and b >= 0):
                    if board[a][b] == 'S':
                        if boy and self.zov:
                            self.zov = False
                            z = []
                            slov.clear()
                        if boy or (m and self.zov):
                            z.append(str(a) + str(b))
                        c = 0
                    elif not (board[a][b] in colors):
                        c+=1
                        boy = True
                        if c == 2:
                            break
                    else:
                        break
                    a+=n
                    b+=g
        if len(z) > 0:
            slov.update({str(i) + str(j): z})
            
    def searchMove(self, board, colors, m = '0'):
        slov = {}
        sign = 1 if colors == 'WC' else -1
        self.zov = True
        if m == '0':
            for i in range(self.size):
                for j in range(self.size):
                    if board[i][j] == colors[0]:
                        self.prov(sign, i, j, board, colors, slov, self.size)
                    if board[i][j] == colors[1]:
                        self.provKing(i, j, board, colors, slov, self.size)
        else:
            if board[int(m[0])][int(m[1])] == colors[0]:
                self.prov(sign, int(m[0]), int(m[1]), board, colors, slov, self.size, False)
            if board[int(m[0])][int(m[1])] == colors[1]:
                self.provKing(int(m[0]), int(m[1]), board, colors, slov, self.size, False)
        return slov
    
    def move(self, board, pawn, move, colors):
        prov = False
        z1 = 1 if int(pawn[0]) < int(move[0]) else -1
        z2 = 1 if int(pawn[1]) < int(move[1]) else -1
        for i in range(1, int(pow((int(pawn[0]) - int(move[0])) ** 2, 0.5))):
            if board[int(pawn[0]) + z1 * i][int(pawn[1]) + z2 * i] != 'S':
                board[int(pawn[0]) + z1 * i][int(pawn[1]) + z2 * i] = 'S'
                if colors[0] == 'B':
                    self.black += 1
                else:
                    self.white += 1
                prov = True
        board[int(move[0])][int(move[1])] = colors[1] if (board[int(pawn[0])][int(pawn[1])] in 'KC') or (move[0] == str(self.size - 1) and colors[0] == 'W') or (move[0] == '0' and colors[0] == 'B') else colors[0]
        board[int(pawn[0])][int(pawn[1])] = 'S'
        return prov
    
    def env(self, player1, player2):
        board = self.board()
        colors = 'WC'
        while(True):
            if self.lim != -1 and self.lim < self.step:
                self.step = 'final'
                if self.black > self.white:
                    return (board, [self.black, self.white], 'BK')
                elif self.black < self.white:
                    return (board, [self.white, self.black], 'WC')
                else:
                    return (board, [self.white, self.black], 'NW')
            if self.black == (self.size // 2) * (self.size // 2 - 1):
                self.step = 'final'
                return (board, [self.black, self.white], 'BK')
            if self.white == (self.size // 2) * (self.size // 2 - 1):
                self.step = 'final'
                return (board, [self.white, self.black], 'WC')
            m = '0'
            while(True):
                slov = self.searchMove(board, colors, m)
                self.step+=1
                if len(slov) == 0 and m == '0':
                    if colors == 'WC':
                        return (board, [self.black, self.white], 'BK')
                    else:
                        return (board, [self.white, self.black], 'WC')
                if len(slov) == 0:
                    break
                (pawn, move) = player1(board, slov, [self.white, self.black], colors) if colors == 'WC' else player2(board, slov, [self.black, self.white], colors)
                if self.move(board, pawn, move, colors):
                    m = move
                    continue
                else:
                    break
            colors = 'BK' if colors == 'WC' else 'WC'

    def printBoard(self, board):
        b = []
        for i in range(1, self.size + 1):
            print(self.size - i, end=' ')
            b.append(i - 1)
            for j in range(0, self.size ):
                print(board[-i][j], end=' ')
            print()
        print('Z',*b)

    def printBoardNew(self, board):
        pygame.init()
        screen = pygame.display.set_mode((50 * self.size, 50 * self.size))
        screen.fill((255, 255, 255))
        for i in range(1, self.size + 1):
            for j in range(0, self.size ):
                pygame.draw.rect(screen, (244, 164, 96) if (i + j) % 2 == 1 else (139, 69, 19), (50 * j, 50 * (i - 1), 50, 50))
                if board[-i][j] in 'BK':
                    pygame.draw.circle(screen, (0, 0, 0), (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2), 23)
                    pygame.draw.circle(screen, (255, 255, 255), (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2), 24, 2)
                if board[-i][j] in 'WC':
                    pygame.draw.circle(screen, (255, 255, 255), (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2), 23)
                    pygame.draw.circle(screen, (64, 64, 64), (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2), 24, 2)
                if board[-i][j] in 'KC':
                    clr = (0, 0, 0) if board[-i][j] == 'C' else (255, 255, 255)
                    pygame.draw.line(screen, clr, (50 * j + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 + 3), (50 * (j) + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 - 3))
                    pygame.draw.line(screen, clr, (50 * j + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 - 3), (50 * (j) + 50 // 2 - 2, 50 * (i - 1) + 50 // 2 + 1))
                    pygame.draw.line(screen, clr, (50 * j + 50 // 2 - 2, 50 * (i - 1) + 50 // 2 + 1), (50 * (j ) + 50 // 2, 50 * (i - 1) + 50 // 2 - 3))
                    pygame.draw.line(screen, clr, (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2 - 3), (50 * (j) + 50 // 2 + 2, 50 * (i - 1) + 50 // 2 + 1))
                    pygame.draw.line(screen, clr, (50 * j + 50 // 2 + 2, 50 * (i - 1) + 50 // 2 + 1), (50 * (j) + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 - 3))
                    pygame.draw.line(screen, clr, (50 * j + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 - 3), (50 * (j) + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 + 3))
                    pygame.draw.line(screen, clr, (50 * j + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 + 3), (50 * (j) + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 + 3))
        pygame.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(52)
                if event.type == pygame.KEYDOWN:
                    running = False

    def printBoardBatch(self, board, url):
        img = Image.new('RGB', (50 * self.size, 50 * self.size), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        for i in range(1, self.size + 1):
            for j in range(0, self.size ):
                draw.rectangle([50 * j, 50 * (i - 1), 50 * (j + 1), 50 * i], fill = (244, 164, 96) if (i + j) % 2 == 1 else (139, 69, 19), width=0)
                if board[-i][j] in 'BK':
                    draw.circle([50 * j + 50 // 2, 50 * (i - 1) + 50 // 2], 24, (0, 0, 0), (255, 255, 255), 2)
                if board[-i][j] in 'WC':
                    draw.circle([50 * j + 50 // 2, 50 * (i - 1) + 50 // 2], 24, (255, 255, 255), (64, 64, 64), 2)
                if board[-i][j] in 'KC':
                    clr = (0, 0, 0) if board[-i][j] == 'C' else (255, 255, 255)
                    draw.line([(50 * j + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 + 3), (50 * (j) + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 - 3),
                               (50 * j + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 - 3), (50 * (j) + 50 // 2 - 2, 50 * (i - 1) + 50 // 2 + 1),
                               (50 * j + 50 // 2 - 2, 50 * (i - 1) + 50 // 2 + 1), (50 * (j ) + 50 // 2, 50 * (i - 1) + 50 // 2 - 3),
                               (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2 - 3), (50 * (j) + 50 // 2 + 2, 50 * (i - 1) + 50 // 2 + 1),
                               (50 * j + 50 // 2 + 2, 50 * (i - 1) + 50 // 2 + 1), (50 * (j) + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 - 3),
                               (50 * j + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 - 3), (50 * (j) + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 + 3),
                               (50 * j + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 + 3), (50 * (j) + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 + 3)],
                               clr, 1)
        if self.step == 'final' or self.step <= self.mxstep:
            img.save(url + '\\' + str(self.step) + '.png')

    def printBoardPlayer(self, board, slov, colors):
        pygame.init()
        screen = pygame.display.set_mode((50 * self.size, 50 * self.size))
        running = True
        prov = [False, False, False]
        pos = (-1, -1)
        move = '-1'
        while running:
            screen.fill((255, 255, 255))
            for i in range(1, self.size + 1):
                for j in range(0, self.size ):
                    pygame.draw.rect(screen, (244, 164, 96) if (i + j) % 2 == 1 else (139, 69, 19), (50 * j, 50 * (i - 1), 50, 50))
                    if board[-i][j] in 'BK':
                        pygame.draw.circle(screen, (0, 0, 0), (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2), 23)
                        if move != str(self.size - i) + str(j):
                            pygame.draw.circle(screen, (255, 255, 255), (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2), 24, 2)
                        else:
                            pygame.draw.circle(screen, (0, 255, 255), (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2), 24, 2)
                    if board[-i][j] in 'WC':
                        pygame.draw.circle(screen, (255, 255, 255), (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2), 23)
                        if move != str(self.size - i) + str(j):
                            pygame.draw.circle(screen, (64, 64, 64), (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2), 24, 2)
                        else:
                            pygame.draw.circle(screen, (0, 255, 255), (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2), 24, 2)
                    if board[-i][j] in 'KC':
                        clr = (0, 0, 0) if board[-i][j] == 'C' else (255, 255, 255)
                        pygame.draw.line(screen, clr, (50 * j + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 + 3), (50 * (j) + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 - 3))
                        pygame.draw.line(screen, clr, (50 * j + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 - 3), (50 * (j) + 50 // 2 - 2, 50 * (i - 1) + 50 // 2 + 1))
                        pygame.draw.line(screen, clr, (50 * j + 50 // 2 - 2, 50 * (i - 1) + 50 // 2 + 1), (50 * (j ) + 50 // 2, 50 * (i - 1) + 50 // 2 - 3))
                        pygame.draw.line(screen, clr, (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2 - 3), (50 * (j) + 50 // 2 + 2, 50 * (i - 1) + 50 // 2 + 1))
                        pygame.draw.line(screen, clr, (50 * j + 50 // 2 + 2, 50 * (i - 1) + 50 // 2 + 1), (50 * (j) + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 - 3))
                        pygame.draw.line(screen, clr, (50 * j + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 - 3), (50 * (j) + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 + 3))
                        pygame.draw.line(screen, clr, (50 * j + 50 // 2 + 4, 50 * (i - 1) + 50 // 2 + 3), (50 * (j) + 50 // 2 - 4, 50 * (i - 1) + 50 // 2 + 3))
                    if prov[1]:
                        for b in slov[move]:
                            #print(b, str(self.size - i) + str(j))
                            if b == str(self.size - i) + str(j):
                                if 50 * j <= pos[0] and pos[0] <= 50 * (j + 1) and  50 * (i - 1) <= pos[1] and pos[1] <=  50 * i:
                                    pawn = str(self.size - i) + str(j)
                                    prov[2] = True
                    if prov[0] and board[-i][j] in colors and slov.get(str(self.size - i) + str(j), 'z') != 'z':
                        if ((pos[0] - (50 * j + 50 // 2)) ** 2 + (pos[1] - (50 * (i - 1) + 50 // 2)) ** 2) ** 0.5 < 23:
                            pygame.draw.circle(screen, (0, 255, 255), (50 * j + 50 // 2, 50 * (i - 1) + 50 // 2), 24, 2)
                            move = str(self.size - i) + str(j)
                            prov[1] = True
            pygame.display.flip()
            if prov[2]:
                return (move, pawn)
            vibor = True
            while vibor:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit(52)
                    if event.type == pygame.MOUSEBUTTONUP:
                        pos = pygame.mouse.get_pos()
                        vibor = False
                        prov[0] = True
        
class Players:
    def __init__(self, env, url = 'null', dstr = False, dbatch = ''):
        self.env = env
        self.url = url
        self.dstr = dstr
        self.dbatch = dbatch
        self.epz = 0
    
    def player(self, board, slov, score, colors):
        self.env.printBoard(board)
        for i in slov:
            print(i + ':', *slov[i])
        while(True):
            print('Введите пешку:')
            pawn = input()
            prov = False
            for i in slov:
                if pawn == i:
                    prov = True
                    break
            if prov:
                break
        while(True):
            print('Введите ход:')
            move = input()
            prov = False
            for i in slov[pawn]:
                if move == i:
                    prov = True
                    break
            if prov:
                break
        return (pawn, move)

    def playerNew(self, board, slov, score, colors):
        return self.env.printBoardPlayer(board, slov, colors)

    def agent_rand(self, board, slov, score = 0, c = 0):
        if self.dstr:
            self.env.printBoardNew(board)
        if self.dbatch != '':
            self.env.printBoardBatch(board, self.dbatch)
        n = random.randint(0, len(slov) - 1)
        m = 0
        for i in slov:
            if m == n:
                pawn = i
                break
            m+=1
        m = 0
        move = slov[pawn][random.randint(0, len(slov[pawn]) - 1)]
        return (pawn, move)
    
    def agent_greedy(self, board, slov, score = 0, c = 0, weight = -1):
        if weight == -1:
            weigth = self.agent_weight(board, slov)
        else:
            weigth = weight
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
        return self.agent_rand(board, best)
                
    def agent_weight(self, board, slov, score = 0, c = 0):
        weigth = {}
        for i in slov:
            colors = 'WC' if board[int(i[0])][int(i[1])] in 'WC' else 'BK'
            z = []
            for j in slov[i]:
                priority = 5
                g = 1 if int(i[0]) - int(j[0]) < 0 else -1
                t = 1 if int(i[1]) - int(j[1]) < 0 else -1
                itr = 0
                danger = False
                vihod = False
                for a in (g, -1 * g):
                    for b in (t, -1 * t):
                        itr+=1
                        if int(j[0]) + a <= len(board) - 1 and int(j[0]) + a >= 0 and int(j[1]) + b <= len(board) - 1 and int(j[1]) + b >= 0:
                            if itr == 1:
                                if board[int(j[0]) + a][int(j[1]) + b] == 'S':
                                    priority+=0
                                elif board[int(j[0]) + a][int(j[1]) + b] in colors:
                                    priority+=0
                                else:
                                    priority-=1
                            if str(itr) in '23':
                                if board[int(j[0]) + a][int(j[1]) + b] == 'S':
                                    priority+=0
                                elif board[int(j[0]) + a][int(j[1]) + b] in colors:
                                    if danger:
                                        priority+=1
                                        danger = False
                                    else:
                                        priority-=0
                                else:
                                    if danger:
                                        priority+=1
                                        danger = False
                                    else:
                                        priority-=1
                                        danger = True
                            if itr == 4:
                                if board[int(j[0]) + a][int(j[1]) + b] == 'S':
                                    priority+=0
                                elif board[int(j[0]) + a][int(j[1]) + b] in colors:
                                    priority+=0
                                else:
                                    priority+=1
                        else:
                            priority = 5 if board[int(j[0]) - g][int(j[1]) - t] in 'S' + colors else 6
                            vihod = True
                            break
                    if vihod:
                        break
                z.append(priority)
            weigth.update({i: z})
        #for i in weigth:
        #    print(i + ':', *weigth[i])
        return weigth

    def usefulness_agent(self, board, slov, score, colors):
        def prov(Q, q):
            for i in range(len(Q)):
                if Q[i][:3] == q:
                    return i
                    break
            return -1
        def reform(color, board, slov):
            new_slov = []
            for i in slov:
                for j in slov[i]:
                    new_slov.append(i+j)
            return [color, board, new_slov]
        Q = []
        try:
            with open(self.url, 'r') as json_file:
                Q = json.load(json_file)
        except:
            print('Error url!')
            exit(52)
        inx = prov(Q, reform(colors, board, slov))
        if inx == -1:
            return self.agent_rand(board, slov)
        else:
            weigth = {}
        for i in slov:
            count = 0
            z = []
            for j in range(len(Q[inx][2])):
                if Q[inx][2][j][:2] == i:
                    count+=1
                    z.append(Q[inx][3][j])
                if count == len(slov[i]):
                    break
            weigth.update({i:z})
        return self.agent_greedy(board, slov, 0, 0, weigth)
    
    def strategy_agent(self, board, slov, score, colors):
        def inx(array, elm):
            for i in range(len(array)):
                if array[i] == elm:
                    return i
            return 'null'
        try:
            with open(self.url, 'r') as json_file:
                J = json.load(json_file)
        except:
            print('Error url!')
            exit(52)
        weigth = {}
        for i in slov:
            z = []
            for j in range(len(slov[i])):
                z.append(-10000)
            weigth.update({i:z})
        for i in J:
            if len(i) >= 5 + 3 * self.epz:
                if i[1] == colors and i[2 + 3 * self.epz] == board and i[3 + 3 * self.epz] != '5252':
                    z = inx(slov[i[3 + 3 * self.epz][:2]], i[3 + 3 * self.epz][2:])
                    if weigth[i[3 + 3 * self.epz][:2]][z] < i[0]:
                        weigth[i[3 + 3 * self.epz][:2]][z] = i[0]
        self.epz+=1
        return self.agent_greedy(board, slov, 0, 0, weigth)

