from datetime import datetime
import random
from PIL import ImageDraw

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
			self.is_marked = False
			self.is_open = False

		def plus(self):
			self.num = self.num + 1

		def mark(self):
			self.is_marked = ~self.is_marked

		def open(self):
			self.is_open = True

		is_marked: bool
		is_open: bool
		is_mine: bool
		num: int  # how many mines are around it

	chat_id: int
	is_ongoing: bool
	board = []
	# board_size = [0, 0]
	times_lost: int
	times_won: int
	mines_left: int  # for player assistance
	cells_left: int

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
		self.mines_left = inp_mines
		self.cells_left = (inp_x * inp_y) - inp_mines
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

	def visualize_board(self):
		pixel = {
			13: [[0, 0, 0, 0, 0], # mine
					[0, 0, 1, 0, 0],
					[0, 1, 1, 1, 0],
					[0, 0, 1, 0, 0],
					[0, 0, 0, 0, 0]],
			12: [[0, 0, 1, 1, 0], # flag
					[0, 0, 1, 1, 0],
					[0, 0, 1, 0, 0],
					[0, 0, 1, 0, 0],
					[0, 0, 1, 0, 0]],
			10: [[0, 0, 0, 0, 0], # unopened
					[0, 1, 1, 1, 0],
					[0, 1, 0, 1, 0],
					[0, 1, 1, 1, 0],
					[0, 0, 0, 0, 0]],
			0: [[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0]],
			1: [[0, 1, 1, 0, 0],
					[0, 0, 1, 0, 0],
					[0, 0, 1, 0, 0],
					[0, 0, 1, 0, 0],
					[0, 0, 1, 0, 0]],
			2: [[0, 1, 1, 1, 0],
					[0, 0, 0, 1, 0],
					[0, 1, 1, 1, 0],
					[0, 1, 0, 0, 0],
					[0, 1, 1, 1, 0]],
			3: [[0, 1, 1, 1, 0],
					[0, 1, 0, 0, 0],
					[0, 1, 1, 1, 0],
					[0, 1, 0, 0, 0],
					[0, 1, 1, 1, 0]],
			4: [[0, 1, 0, 1, 0],
					[0, 1, 0, 1, 0],
					[0, 1, 1, 1, 0],
					[0, 0, 0, 1, 0],
					[0, 0, 0, 1, 0]],
			5: [[0, 1, 1, 1, 0],
					[0, 1, 0, 0, 0],
					[0, 1, 1, 1, 0],
					[0, 0, 0, 1, 0],
					[0, 1, 1, 1, 0]],
			6: [[0, 1, 1, 1, 0],
					[0, 1, 0, 0, 0],
					[0, 1, 1, 1, 0],
					[0, 1, 0, 1, 0],
					[0, 1, 1, 1, 0]],
			7: [[0, 1, 1, 1, 0],
					[0, 0, 0, 0, 1],
					[0, 0, 0, 1, 0],
					[0, 0, 1, 0, 0],
					[0, 1, 0, 0, 0]],
			8: [[0, 1, 1, 1, 0],
					[0, 1, 0, 1, 0],
					[0, 1, 1, 1, 0],
					[0, 1, 0, 1, 0],
					[0, 1, 1, 1, 0]]}
		SCALE = 1
		BORDER = 1

		for line in self.board: # x ++
			loc_x = enumerate(line)
			for cell in line: # y ++
				loc_y = enumerate(cell)
				if cell.is_open:
					if cell.is_mine:
						pass # 13
					match cell.num:
						case 0:
							pass
						case 1:
							pass
						case 2:
							pass
						case 3:
							pass
						case 4:
							pass
						case 5:
							pass
						case 6:
							pass
						case 7:
							pass
						case 8 :
							pass
				elif cell.is_marked:
					pass  # 12
				else:
					pass #10

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
		if ~self.board[x][y].is_marked & ~self.board[x][y].is_open:
			if self.board[x][y].is_mine:
				self.gameover()
			else:
				self.board[x][y].open()
				self.cells_left -= 1
		if self.cells_left.__eq__(0):
			self.victory()

	def mark_cell(self, x: int, y: int):
		self.board[x][y].mark()
		self.mines_left -= 1

	def command_receiver(self, command: int, inp_x: int, inp_y: int):
		if command.__eq__(0):  # start new game
			pass
		elif self.is_ongoing:
			if command.__eq__(1):  # open cell
				self.open_cell(inp_x, inp_y)
			if command.__eq__(2):  # mark cell
				self.mark_cell(inp_x, inp_y)
		else:  # game not started, start new game?
			pass
# inputs :
#  start game
#  open cell
#  mark cell
# output:
#  text
#  image
#  ammounts
