import logging
import string
import token

from datetime import datetime
import random

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from PIL import Image
from io import BytesIO

t_o_k_e_n = None

enable_logging = False


def gen_rand_int(min_val: int, max_val: int):
	random.seed(datetime.now())
	ret_res = random.random() * (max_val - 1) + min_val
	if ret_res - int(ret_res) >= 0.5:
		return int(ret_res) + 1
	# elif ret_res - int(ret_res) < -0.5:  # probably useless
	# return int(ret_res) - 1
	else:
		return int(ret_res)


# roll die casted as roll [number of dies]d[number of sides]
def roll(inp_t: str):
	hm_sides: int = 0
	hm_dies: int = 0
	result: str = ""
	total = 0
	# get number of sides and dies from string [number of dies]d[number of sides]
	inp_t = inp_t[inp_t.find("roll") + 5:]
	if inp_t.__contains__(" "):
		inp_t = inp_t[:inp_t.find(" ")]
	print(inp_t)
	# should be a pure die at this point
	if inp_t.__contains__("d"):
		aaa = inp_t.find("d")
		hm_sides = int(inp_t[aaa + 1:])
		hm_dies = int(inp_t[:aaa])
	else:
		return "no die found"

	result = "Rolling " + str(hm_dies) + " dies with " + str(hm_sides) + " sides \n"
	for i in range(0, hm_dies):
		side = gen_rand_int(1, hm_sides)
		total += side
		result += str(side) + " ,  "
	result = result[:-4]
	result += ".\nTotal is " + str(total)
	return result


################## handlers go right here #############################
class Game:
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
	is_started: bool
	is_lost: bool
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
	def generate_board(self, inp_x: int, inp_y: int):
		mine_list = self.generate_mines(inp_x, inp_y, 1)
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
		c_x = 0
		while c_x < inp_x:
			c_y = 0
			while c_y < inp_y:  # shitty code but I can't be bothered
				# Adds +1 to every cell near mine#
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

	def game_start(self, x: int, y: int, mines):
		self.is_lost = False

		self.is_started = True
		pass

	def gameover(self):
		self.is_lost = True
		pass

	def open_cell(self, x: int, y: int):
		pass


def start(update: Update, context: CallbackContext) -> None:
	update.message.reply_text(
		"Hi! I'm a prototype. Here are some commands I understand:\n"
		"1. /start - Show this message\n"
		"2. /help - Help on usage")


def he_p(update: Update, context: CallbackContext):
	update.message.reply_text(
		"To convert n image into a different format, follow these simple steps:\n"
		"1. Attach an image to your reply\n"
		"2. Send the image\n"
		"3. Type in one of the following commands:\n"
		" /png - Convert picture to PNG\n"
		" /jpg - Convert picture to JPG\n"
		" /webp - Convert picture to WEBP\n")
	pass


################################ images handling ############################
######### save/load #########


# format { chat/user : image }
image_dictionary = {}


def mtb_save_image(update: Update, context: CallbackContext):
	mtb_bytes = bytes(context.bot.get_file(update.message.photo[-1].file_id).download_as_bytearray())
	print(mtb_bytes)
	image_dictionary.update({update.message.chat.id: mtb_bytes})


def handle_message_other(update: Update, context: CallbackContext):
	if update.message.document:  # download if has webp Document
		mtb_doc = update.message.document
		if mtb_doc.file_name[-4:].__eq__("webp"):
			mtb_bytes = bytes(update.message.document.get_file().download_as_bytearray())
			print(mtb_bytes)
			image_dictionary.update({update.message.chat.id: mtb_bytes})
		else:
			update.message.reply_text("File type not recognized, try sending as picture")
	message_text = update.message.text.lower()
	message_text
	if message_text.__contains__('roll'):
		update.message.reply_text(roll(message_text))
		return


##############################

def universal_converter(update: Update, img_type: str):
	if image_dictionary.get(update.message.chat.id) is None:
		return None
	else:
		mtb_bytes = BytesIO()
		mtb_img = Image.open(BytesIO(image_dictionary.get(update.message.chat.id)))
		mtb_img.save(mtb_bytes, format=img_type)
		mtb_bytes.seek(0)
		mtb_img = mtb_bytes.read()
		return mtb_img


def to_jpg(update: Update, context: CallbackContext):
	result = universal_converter(update, "jpeg")
	if result is None:
		update.message.reply_text("No image found")
	else:
		update.message.reply_text(
			"You may probably just download your own photo now.\n"
			"Telegram converts them to JPEG automatically.")
		update.message.reply_document(document=result)


def to_webp(update: Update, context: CallbackContext):
	result = universal_converter(update, "webp")
	if result is None:
		update.message.reply_text("No image found")
	else:
		update.message.reply_document(document=result)


def to_png(update: Update, context: CallbackContext):
	result = universal_converter(update, "png")
	if result is None:
		update.message.reply_text("No image found")
	else:
		# update.message.reply_photo(photo=result)
		update.message.reply_document(document=result)


####################################################
#	def msg_is(inp):
#		return update.message.text.__eq__(inp)
#####################################################
#	def msg_has(inp):  # contains text?
#		return update.message.text.__contains__(inp)
#####################################################
#	def reply(inp):  # text reply
#		update.message.reply_text(inp)
#####################################################


def handlers_setup(dispatcher: Updater.dispatcher):
	dispatcher.add_handler(CommandHandler("start", start))
	dispatcher.add_handler(CommandHandler("help", he_p))
	dispatcher.add_handler(CommandHandler("png", to_png))
	dispatcher.add_handler(CommandHandler("jpg", to_jpg))
	dispatcher.add_handler(CommandHandler("webp", to_webp))
	dispatcher.add_handler(MessageHandler(Filters.photo & ~Filters.command, mtb_save_image))
	dispatcher.add_handler(MessageHandler(~Filters.command, handle_message_other))


# dispatcher.add_handler(MessageHandler(Filters.command, ))


def main():
	updater = Updater(t_o_k_e_n)
	handlers_setup(updater.dispatcher)
	updater.start_polling()
	updater.idle()


if __name__ == "__main__":
	if t_o_k_e_n is None:
		t_o_k_e_n = token.token
	if enable_logging:
		logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
		logger = logging.getLogger(__name__)
	main()
