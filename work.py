from neyro import *
boy = Environment(4)
player1 = Players(boy)
player2 = Players(boy)
player1 = Players(boy, 'Agents\\qlerning4.json', dstr = True, dbatch = 'Images')
#player2 = Players(boy, 'Agents\\oppositionqlerning.json', dstr = True, dbatch = False)
player2 = Players(boy, 'Agents\\nstepqlerning4.json', dstr = True, dbatch = 'Images')
#player2 = Players(boy, 'Agents\\doubleqlerning.json', dstr = True)
board = boy.env(player1.usefulness_agent, player2.usefulness_agent)[0]
boy.printBoardNew(board)
boy.printBoardBatch(board, 'Images')
pygame.quit()
