# Документация

!!! Все неупомянутые методы служебные !!!

neyro.py - файл со средой и агентами

Класс среды:

	Environment(size = 8, maximg = 20, lim = -1) - класс среды:
	
		size - размер стороны доски
	 
		maximg - лимит для printBoardBatch
	 
		lim - лимит ходов (-1 безлимитные ходы)
	 
		Environment.env(player1,player2):
	 
			player1 - функция агента белых
	  
			player2 - функция агента черных
	  
			Метод возвращает (доска, [очки победителя, очки проигравшего], цвет победителя)
	  
		Environment.printBoard(board):
	 
			Выводит доску в консоль (старый вид)
	  
		Environment.printBoardNew(board):
	 
			Визуализирует доску. Любая кнопка, чтобы пролистнуть
	  
		Environment.printBoardBatch(board, url):
	 
			Создает картинки доски в папку  адресу url
	  
			вплоть до maximg экземпляров
	  
Класс агентов:
 
	Players(env, url = 'null', dstr = False, dbatch = False) - класс агентов:
	
		env - екземпляр класса доски
	 
		url - путь до обученного агента
	 
		dstr - вывод визуализации
	 
		dbatch - создание картинок доски
	 
!!! Все аргументы методов чисто технические, нужно просто передавать ссылку на метод в Environment.env(player1,player2) !!!
	
		Players.player(board, slov, score = 0, c = 0):
	 
			Метод для взаимодействие игрока (человека) со средой (старый интерфейс)
	  
		Players.playerNew(board, slov, score, colors):
	 
			Метод для взаимодействие игрока (человека) со средой (новый интерфейс)
	  
		Players.agent_rand(board, slov, score = 0, c = 0):
	 
			Метод рандомного алгоритма
	  
		Players.agent_weight(board, slov, score = 0, c = 0):
	 
			Метод немного умного алгоритма, который смотрит на 1 шаг в перед
	  
		Players.usefulness_agent(board, slov, score, colors):
	 
			Метод, для использования любого алгоритма RL основанного на полезности (все кроме Reinforce)
	  
		Players.strategy_agent(board, slov, score, colors):
	 
			Метод, для использования любого алгоритма RL основанного на стратегиях (только Reinforce)
	  
	
lerning.py - файл с реализацией алгоритмов обучения

Классы алгоритмов обучения:

 
	Часто поподающиеся аргументы:
	
		size - размер доски (рекомендую 4, остальное просто не потянет)
	 
		agent - выбор алгоритма на котором происходит обучение (True - рандомный, False - немного умный)
	 
		N - количество игр
	 
		a - скорость обучения
	 
		y - влияние последующих вознаграждений
	 
		url - адресс агента для обучения
	 
	Все интерфейсные методы (справедливо для всех классов):
	
		Class.learning(progress = False, аргументы конструктора):
	 
			Метод начала обучения (есть возможность дообучить, поменять аргументы класса)
	  
			progress - вывод прогресса обучения в консоль (Reinforce несовершенен)
	  
		Class.win_rate(N, agent):
	 
			Метрика побед на N игр
	  
			agent - выбор алгоритма как противника (также только 2 варианта)
	  
		Class.save(file):
	 
			Сохраняет агента по file. Cтрого .json файл
	  
		Class.print_weigths():
	 
			Выводит в консоль Q-функции и т.п.
	  
	Qlerning(size, agent, N, a = 0.1, y = 0.9, url = '') - реализация Q-обучения
	
	Sarsa(size, agent, N, a = 0.1, y = 0.9, url = '') - реализация SARSA
	
	Reinforce(size, agent, N, y = 0.9, url = '') - упрощенная реализация Reinforce (детермизированная политика)
	
	Double_Qlerning(size, agent, N, a = 0.1, y = 0.9, url = '') - реализация двойного Q-обучения
	
	Deferred_Qlerning(self, size, agent, N, m = 5, a = 0.1, y = 0.9, url = '') - реализация отложенного Q-обучения
	
		m - требование к количеству попаданий на связку s - a, для обновления Q-функции
	 
	Opposition_Qlerning(self, size, agent, N, p = 0.1, a = 0.1, y = 0.9, url = '') - реализация Q-обучения на противодействии:
	
		p - шанс выполнения действия с минимальной полезностью
	 
	Nstep_Qlerning(size, agent, N, n = 2, a = 0.1, y = 0.9, url = '') - реализация n-арного алгоритма
	
		n - количество шагов видимости
	 
	Watkins_Qlerning(size, agent, N, a = 0.1, y = 0.9, url = '') - реализация алгоритма Уоткинса
	
	FuzEras_Watkins_Qlerning(size, agent, N, mstep = 5, a = 0.1, y = 0.9, url = '') - алгоритм Уоткинса, с нечеткими стираниями
		mstep - условие стирания (моя реализация - кол-во шагов с стиранием)
	Fast_Qlerning(size, agent, N, a = 0.1, y = 0.9, url = '') - реализация быстрого Q-обучения

work.py - файл с примером
