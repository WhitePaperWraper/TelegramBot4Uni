import json
import logging
import random
import urllib.parse
import urllib.request
from datetime import datetime
from io import BytesIO

from PIL import Image
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

import tokenOfTheBot

t_o_k_e_n = None
cat_api_token = None

enable_logging = False
ram_economy = False

image_dictionary = {}

query_dictionary = {}

main_menu = [
	[
		InlineKeyboardButton("Option 1", callback_data="1"),
		InlineKeyboardButton("Quote", callback_data="quote"),
	],
	[
		InlineKeyboardButton("Get a cat", callback_data="cat"),
		InlineKeyboardButton("Convert", callback_data="convert")
	]
]



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


# format { chat/user : image }


def mtb_save_image(update: Update, context: CallbackContext):
	if not ram_economy:
		mtb_bytes = bytes(context.bot.get_file(update.message.photo[-1].file_id).download_as_bytearray())
		image_dictionary.update({update.message.chat.id: mtb_bytes})
		print(update.message.chat.id)
	else:
		update.message.reply_text("Image conversion is disabled right now for RAM economy")


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
	if message_text.__contains__('roll'):
		update.message.reply_text(roll(message_text))
		return


##############################

def universal_converter(chat_id, img_type: str):
	print(chat_id)
	if image_dictionary.get(chat_id) is None:
		return None
	else:
		mtb_bytes = BytesIO()
		mtb_img = Image.open(BytesIO(image_dictionary.get(chat_id)))
		mtb_img.save(mtb_bytes, format=img_type)
		mtb_bytes.seek(0)
		mtb_img = mtb_bytes.read()
		return mtb_img
################## handlers go right here ############################



def start(update: Update, context: CallbackContext) -> None:
	update.message.reply_text(
		"Hi! I'm a prototype. Here are some commands I understand:\n"
		"1. /start - Show this message\n"
		"2. /help - Help on usage\n0"
		"3. /cat - for a cat")


def st_rt(update: Update, context: CallbackContext) -> None:
	keyboard = main_menu
	query_dictionary.update(query_dictionary|{update.message.chat.id: keyboard})
	reply_markup = InlineKeyboardMarkup(query_dictionary.get(update.message.chat.id))

	update.message.reply_text("Please choose:", reply_markup=reply_markup)


def button(update: Update, context: CallbackContext):
	query = update.callback_query
	chat_id = query.message.chat.id
	query.answer()
	if not query_dictionary.keys().__contains__(chat_id):
		query_dictionary.update(query_dictionary|{chat_id: main_menu})
	query.edit_message_text(text=f"Selected option: {query.data}")
	if query.data.__eq__("cat"):
		with urllib.request.urlopen("https://api.thecatapi.com/v1/images/search") as link:
			response = json.loads(link.read().decode())
		query.message.chat.send_photo(response[0]['url'])
	if query.data.__eq__("convert"):
		query_dictionary[query.message.chat.id] = [
			[InlineKeyboardButton("To Png", callback_data="png")],
			[InlineKeyboardButton("To webp", callback_data="webp")],
			[InlineKeyboardButton("Go back", callback_data="menu")]
			]
	if query.data.__eq__("menu"):
		query_dictionary[chat_id] = main_menu
	if query.data.__eq__("png"):
		result = universal_converter(chat_id, "png")
		if result is None:
			query.message.chat.send_message("No image found")
		else:
			query.message.chat.send_document(document=result)
	if query.data.__eq__("webp"):
		result = universal_converter(chat_id, "webp")
		if result is None:
			query.message.chat.send_message("No image found")
		else:
			query.message.chat.send_document(document=result)
	if query.data.__eq__("quote"):
		payload = {'method': 'getQuote', 'format': 'json', 'lang': 'ru'}
		url = "https://api.forismatic.com/api/1.0"
		urlother = "https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=ru"
		req = urllib.request.Request(urlother, headers={'User-Agent': "Magic Browser"})
		with urllib.request.urlopen(req) as link:
			response = json.loads(link.read().decode())
			print(response)
		query.message.chat.send_message(text = response['quoteText']+"\n\n"+response["quoteAuthor"])
	reply_markup = InlineKeyboardMarkup(query_dictionary.get(chat_id))
	query.message.chat.send_message("Please choose:", reply_markup=reply_markup)



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

def cat(update: Update, context: CallbackContext):
	with urllib.request.urlopen("https://api.thecatapi.com/v1/images/search") as link:
		response = json.loads(link.read().decode())
	#print(response)
	update.message.reply_photo(response[0]['url'])

################################ images handling ############################
######### save/load #########





def to_jpg(update: Update, context: CallbackContext):
	result = universal_converter(update.message.chat.id, "jpeg")
	if result is None:
		update.message.reply_text("No image found")
	else:
		update.message.reply_text(
			"You may probably just download your own photo now.\n"
			"Telegram converts them to JPEG automatically.")
		update.message.reply_document(document=result)


def to_webp(update: Update, context: CallbackContext):
	result = universal_converter(update.message.chat.id, "webp")
	if result is None:
		update.message.reply_text("No image found")
	else:
		update.message.reply_document(document=result)


def to_png(update: Update, context: CallbackContext):
	result = universal_converter(update.message.chat.id, "png")
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
	dispatcher.add_handler(CommandHandler("start", st_rt))
	dispatcher.add_handler(CallbackQueryHandler(button))
	#dispatcher.add_handler(CommandHandler("help", he_p))
	#dispatcher.add_handler(CommandHandler("cat", cat))
	#dispatcher.add_handler(CommandHandler("png", to_png))
	#dispatcher.add_handler(CommandHandler("jpg", to_jpg))
	#dispatcher.add_handler(CommandHandler("webp", to_webp))
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
	if cat_api_token is None:
		cat_api_token = tokenOfTheBot.cat_api
	if enable_logging:
		logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
		logger = logging.getLogger(__name__)
	main()
