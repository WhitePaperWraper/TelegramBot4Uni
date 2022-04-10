from datetime import datetime
import random


def gen_rand_int(min_val: int, max_val: int):
	random.seed(datetime.now())
	ret_res = random.random() * (max_val - 1) + min_val
	if ret_res - int(ret_res) >= 0.5:
		return int(ret_res) + 1
	# elif ret_res - int(ret_res) < -0.5:  # probably useless
	# return int(ret_res) - 1
	else:
		return int(ret_res)


game_dictionary = {}


class Minesweeper:
	class Cell:
		def __init__(self, i_is_mine, i_num=0):
			self.is_mine = i_is_mine
			self.num = i_num

		def plus(self):
			self.num = self.num + 1

		is_open: bool
		is_mine: bool
		num: int  # how many mines are around it

	chat_id: int
	is_ongoing: bool
	board = []
	# board_size = [0, 0]
	times_lost: int
	times_won: int
	mines = 0  # for player assistance

	def ratio(self):
		if self.times_lost:
			return self.times_won / self.times_lost
		else:
			return self.times_won

	def print_board(self):
		pass

	@staticmethod
	def generate_mines(size_x: int, size_y: int, amnt: int):
		def gen_mine(max_x, max_y):
			mine = [gen_rand_int(0, max_x), gen_rand_int(0, max_y)]
			return mine

		mine_list = []
		while amnt > 0:
			mine = gen_mine(size_x, size_y)
			while mine in mine_list:
				mine = gen_mine(size_x, size_y)
			mine_list = mine_list + mine
		return mine_list

	# x->1,2,3,4
	# y
	# |
	# \/
	# 1  [][][][]
	# 2  [][][][]
	# 3  [][][][]
	# 4  [][][][]
	def generate_board(self, inp_x: int, inp_y: int, inp_mines: int):
		mine_list = self.generate_mines(inp_x, inp_y, inp_mines)
		board = [[self.Cell(False) for y in range(inp_y)] for x in range(inp_x)]
		# I THINK above is right? Python SUUUUUUUUUUUUUCKS at 2d arrays
		inp_x -= 1  # adjustment for array indexing, to use as max index
		inp_y -= 1  # adjustment for array indexing, to use as max index
		# generating cells in two-dimensional array, column at a time
		c_x = 0
		while c_x < inp_x:
			c_y = 0
			while c_y < inp_y:
				board[c_x][c_y] = self.Cell([c_x, c_y] in mine_list)
				c_y += 1
			c_x += 1
		############
		# shitty code but I can't be bothered
		# Adds +1 to every cell near mine, I think. Maybe it just summons demons
		c_x = 0
		while c_x < inp_x:
			c_y = 0
			while c_y < inp_y:
				if board[c_x][c_y].is_mine:
					if c_x + 1 <= inp_x & c_x & c_y & c_y + 1 <= inp_y:
						board[c_x - 1][c_y - 1].plus()
						board[c_x - 1][c_y].plus()
						board[c_x - 1][c_y + 1].plus()
						board[c_x][c_y - 1].plus()
						board[c_x][c_y + 1].plus()
						board[c_x + 1][c_y - 1].plus()
						board[c_x + 1][c_y].plus()
						board[c_x + 1][c_y + 1].plus()
					else:
						if c_x:  # if cell is near left wall
							if c_y:
								board[c_x][c_y + 1].plus()
								board[c_x + 1][c_y].plus()
								board[c_x + 1][c_y + 1].plus()
							elif c_y + 1 <= inp_y:
								board[c_x + 1][c_y - 1].plus()
								board[c_x + 1][c_y].plus()
								board[c_x][c_y - 1].plus()
							else:
								board[c_x + 1][c_y - 1].plus()
								board[c_x + 1][c_y].plus()
								board[c_x + 1][c_y + 1].plus()
								board[c_x][c_y - 1].plus()
								board[c_x][c_y + 1].plus()
						elif c_x + 1 <= inp_x:  # if cell is near right wall, just replace + with minus
							if c_y:
								board[c_x][c_y + 1].plus()
								board[c_x - 1][c_y].plus()
								board[c_x - 1][c_y + 1].plus()
							elif c_y + 1 <= inp_y:
								board[c_x - 1][c_y - 1].plus()
								board[c_x - 1][c_y].plus()
								board[c_x][c_y - 1].plus()
							else:
								board[c_x - 1][c_y - 1].plus()
								board[c_x - 1][c_y].plus()
								board[c_x - 1][c_y + 1].plus()
								board[c_x][c_y - 1].plus()
								board[c_x][c_y + 1].plus()
						elif c_y:  # not near wall but near top/bottom
							board[c_x - 1][c_y].plus()
							board[c_x - 1][c_y + 1].plus()
							board[c_x][c_y + 1].plus()
							board[c_x + 1][c_y].plus()
							board[c_x + 1][c_y + 1].plus()
						else:  # near the other wall
							board[c_x - 1][c_y - 1].plus()
							board[c_x - 1][c_y].plus()
							board[c_x][c_y - 1].plus()
							board[c_x + 1][c_y - 1].plus()
							board[c_x + 1][c_y].plus()

				#################################FUCKING ATROCIOUS###########################################

				c_y += 1
			c_x += 1
		self.board = board

	def game_start(self, x: int, y: int, mines):
		self.generate_board(x, y, mines)
		self.is_ongoing = True
		pass

	def gameover(self):
		self.times_lost += 1
		self.is_ongoing = False
		pass

	def victory(self):
		self.times_won += 1
		self.is_ongoing = False
		pass

	def open_cell(self, x: int, y: int):
		pass