import logging
import tokenOfTheBot

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


################## handlers go right here ############################

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
		t_o_k_e_n = tokenOfTheBot.token
	if enable_logging:
		logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
		logger = logging.getLogger(__name__)
	main()
