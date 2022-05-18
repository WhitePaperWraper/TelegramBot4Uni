from datetime import datetime
import random
from PIL import Image, ImageDraw

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
				board[c_x][c_y] = self.Cell([c_x, c_y] in mine_list)#passing bool, setting cell as mine or as empty
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
					#0 1  2  3 <-x
					#1[0][1][2]
					#2[3][#][4]
					#3[5][6][7]
					exists = [True, True, True, True, True, True, True, True]
					if c_x: # if cell is near left wall e.g. x equal = 0
						exists[0] = False
						exists[3] = False
						exists[5] = False
					if c_y: # if y = 0
						exists[0] = False
						exists[1] = False
						exists[2] = False
					if c_x + 1>inp_x: # if y = 0
						exists[2] = False
						exists[4] = False
						exists[7] = False
					if c_y + 1>inp_y: # if
						exists[5] = False
						exists[6] = False
						exists[7] = False

					if exists[0]:
						board[c_x - 1][c_y - 1].plus()
					if exists[1]:
						board[c_x][c_y - 1].plus()
					if exists[2]:
						board[c_x + 1][c_y - 1].plus()
					if exists[3]:
						board[c_x - 1][c_y].plus()
					if exists[4]:
						board[c_x + 1][c_y].plus()
					if exists[5]:
						board[c_x - 1][c_y + 1].plus()
					if exists[6]:
						board[c_x][c_y + 1].plus()
					if exists[7]:
						board[c_x + 1][c_y + 1].plus()
					#############################
				c_y += 1
			c_x += 1
		self.board = board

	def visualize_board(self):
		#needed figures:
		# closed field
		# open empty field
		# numbers 1-8
		# flag
		# mine(detonated)
		# mine(revealed)
		cell_size = 100
		board_width = cell_size * len(self.board[0])
		board_length = cell_size*len(self.board)
		visual_map = Image.new('RGB', (board_width, board_length))#x then y ?
		board = ImageDraw.Draw(visual_map)
		board.rectangle([0, 0, board_width, board_length], fill=[150, 150, 150], width=0)
		def draw_cell(i_loc_x, i_loc_y):
			if self.board[i_loc_x][i_loc_y].is_open:
				#draw open field
				if self.board[i_loc_x][i_loc_y].is_mine:
					pass # draw red mine
				elif self.board[i_loc_x][i_loc_y].num.__eq__(0):
					pass#draw empty field
				elif self.board[i_loc_x][i_loc_y].num.__eq__(1):
					pass#draw 1
				elif self.board[i_loc_x][i_loc_y].num.__eq__(2):
					pass#draw 2
				elif self.board[i_loc_x][i_loc_y].num.__eq__(3):
					pass#draw 3
				elif self.board[i_loc_x][i_loc_y].num.__eq__(4):
					pass#draw 4
				elif self.board[i_loc_x][i_loc_y].num.__eq__(5):
					pass#draw 5
				elif self.board[i_loc_x][i_loc_y].num.__eq__(6):
					pass#draw 6
				elif self.board[i_loc_x][i_loc_y].num.__eq__(7):
					pass#draw 7
				elif self.board[i_loc_x][i_loc_y].num.__eq__(8):
					pass#draw 8
			elif self.board[i_loc_x][i_loc_y].is_marked:
				pass #draw flag
			else:
				pass # draw closed field

		for loc_x, line in enumerate(self.board): # x ++
			for loc_y, cell in enumerate(line): # y ++
				draw_cell(loc_x, loc_y)

	def game_start(self, x: int, y: int, mines):
		self.generate_board(x, y, mines)
		self.is_ongoing = True
		pass

	def gameover(self):
		self.times_lost += 1
		for line in self.board: # open all cells with mines
			for cell in line:
				if cell.is_mine:
					cell.open()
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
