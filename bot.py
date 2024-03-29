import telebot
import os
import time

from config import token, my_id
from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

def two_fact():	#Ввод кода двухфакторной аутентификации в чате бота

	global auth_args
	auth_args = []
	
	global handler_mode
	handler_mode = 'two_factor'
	
	bot.send_message(my_id, 'СЛЫШ ВВОДИ КОД ИЛИ ЦИФРЫ НОМЕРА ТЕЛЕФОНА') #Приглашаем пользователя (меня) ввести код
	
	bot.polling() #Ожидаем
	
	bot.send_message(my_id, 'ПРИНЯТО')
	auth_args.append(False) #Второй аргумент
	return auth_args

def cap_handl(captcha):

	global auth_args
	auth_args = []

	global handler_mode
	handler_mode = 'captcha'

	bot.send_document(my_id, captcha.get_url(), 'СЛЫШ ВВОДИ С КАРТИНКИ') #Приглашаем пользователя (меня) ввести капчу

	bot.polling() #Ожидаем

	bot.send_message(my_id, 'ПРИНЯТО')

	captcha.try_again(key=auth_args[0])
	
def fix_html(text):
	text = text.replace('<', '&lt')
	text = text.replace('>', '&gt')
	return text
	
def alarm(ex, link = None):
	print(str(ex))
	time.sleep(60)
	if link is None:
		text = "EXCEPTION: " + fix_html(str(ex))
	else:
		text = "EXCEPTION. Ошибка при отправке поста " + link + '\n\n' + fix_html(str(ex))
	send_even_long_message(text)

def send_post(post):
	album = []
	audios = []
	animations = []
	docs = []
	
	for item in post.media:
		if item.type == 'photo':
			album.append(InputMediaPhoto(item.link))
		elif item.type == 'video':
			post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется видосик: ' + create_href(item.link, item.title)
		elif item.type == 'audio':
			audios.append(item)
		elif item.type == 'gif':
			animations.append(item)
		elif item.type == 'doc':
			docs.append(item)
		elif item.type == 'link':
			post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, прикреплена ссылка: ' + create_href(item.link, item.title)
		elif item.type == 'playlist':
			post.text += '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется плейлист ' + create_href(item.link, item.title)
		elif item.type == 'poll':
			post.text += '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется ' + item.link
		elif item.type == 'wiki':
			post.text += '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется вики-страница: ' + create_href(item.link, item.title)
		elif item.type == 'album':
			post.text += '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется фотоальбом: ' + item.title
		elif item.type == 'market':
			post.text += '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется товар: ' + item.title
		elif item.type == 'market_album':
			post.text += '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется подборка: ' + item.title + ' товаров'
		elif item.type == 'event':
			post.text += '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется встреча: ' + item.title
		
			
	if len(audios) > 0:
		post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеются аудио:\n'
		for audio in audios:
			post.text = post.text + audio.author + ' - ' + audio.title + '\n'

	try:
		if len(animations) > 0:
			post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеются гифки\n'
			for gif in animations:
				bot.send_document(my_id, gif.link)
		
		if len(docs) > 0:
			post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеются докУменты\n'
			for doc in docs:
				bot.send_document(my_id, doc.link)
	except Exception as e:
		alarm(e, create_href(post.link, post.source_name))

	try:
		if len(album) == 0:
			send_even_long_message(post.text, markup = create_markup(post.link[19:]))
		else:
			if len(post.text) < 1024:
				album[0].caption = post.text
				album[0].parse_mode = 'HTML'
				messages = bot.send_media_group(my_id, album)
				first = messages[0].message_id #id первой фотки
				last = messages[-1].message_id #id последней фотки
				try:
					bot.edit_message_reply_markup(my_id, last, reply_markup = create_markup(post.link[19:]))
				except Exception:
					bot.edit_message_caption('', chat_id = my_id, message_id = first)
					send_even_long_message(post.text, markup = create_markup(post.link[19:]))
			else:
				bot.send_media_group(my_id, album)
				send_even_long_message(post.text, markup = create_markup(post.link[19:]))
	except Exception as e:
		alarm(e, create_href(post.link, post.source_name))
	
def create_markup(data, liked = 0):
	markup = InlineKeyboardMarkup()
	if liked == 0:
		markup.row(InlineKeyboardButton('Лайк', callback_data = 'ln' + data), InlineKeyboardButton('Pocket', callback_data = 'p' + data))
	elif liked == 1:
		markup.row(InlineKeyboardButton('Лайкнуто', callback_data = 'ly' + data), InlineKeyboardButton('Pocket', callback_data = 'p' + data))
	else:
		markup.row(InlineKeyboardButton('Удалено', callback_data = 'ld' + data), InlineKeyboardButton('Pocket', callback_data = 'p' + data))
	return markup
	
def send_even_long_message(text, markup = None):
	while len(text) > 4096:
		bot.send_message(my_id, text[0:4096], parse_mode = 'HTML')
		text = text[4096:]
	return bot.send_message(my_id, text, parse_mode = 'HTML', reply_markup = markup).message_id

handler_mode = ''
auth_args = [] #Лист аргументов для функции

bot = telebot.TeleBot(token) 
print(bot.get_me()) #Проверка, что работает

upd = bot.get_updates()
if len(upd) > 0:
	bot.get_updates(upd[-1].update_id + 1) #Пропускаем всё, что пришло, пока бот лежал
	
@bot.message_handler(content_types=['text']) #Штука, которая примет код
def handle_everything(message):
	if message.from_user.id == my_id:
		if handler_mode == 'two_factor':
			auth_args.append(message.text)
			bot.delete_message(my_id, message.message_id)
			bot.stop_polling() #Выключаем ожидание
		elif handler_mode == 'captcha':
			auth_args.append(message.text)
			bot.delete_message(my_id, message.message_id)
			bot.stop_polling() #Выключаем ожидание
		elif handler_mode == 'log_pass':
			auth_args.extend(message.text.split('\n', 2))
			bot.delete_message(my_id, message.message_id)
			bot.stop_polling() #Выключаем ожидание
		elif handler_mode == 'check_down':
			if ('упал' in message.text.lower()) and (message.text[-1] == '?'):
				bot.send_message(my_id, 'Не упал')
			elif 'падай' in message.text.lower():
				bot.send_photo(my_id, 'https://pbs.twimg.com/media/DwVI7QBWkAEsY1g.jpg')
				os._exit(0)

def create_href(link, text):
	return '<a href=\"' + link + '\">' + text + '</a>'
	
def get_log_pass():
	global auth_args
	auth_args = []
	
	global handler_mode
	handler_mode = 'log_pass'
	
	bot.send_message(my_id, 'СЛЫШ ВВОДИ ИХ') #Приглашаем пользователя (меня) ввести
	
	bot.polling() #Ожидаем
	
	bot.send_message(my_id, 'ПРИНЯТО')
	return auth_args

def check_down():
	global handler_mode
	handler_mode = 'check_down'
	
	while True:
		try:
			bot.polling(none_stop = True, interval = 0, timeout = 20)
		except Exception as e:
			alarm(e)