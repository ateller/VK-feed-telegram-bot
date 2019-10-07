import telebot
import os
import time

from telebot import apihelper
from config import token, prox_ip, my_id
from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

def two_fact():	#Ввод кода двухфакторной аутентификации в чате бота

	global auth_args
	auth_args = []
	
	global handler_mode
	handler_mode = 'two_factor'
	
	bot.send_message(my_id, 'СЛЫШ ВВОДИ') #Приглашаем пользователя (меня) ввести код
	
	bot.polling() #Ожидаем
	
	bot.send_message(my_id, 'ПРИНЯТО')
	auth_args.append(False) #Второй аргумент
	return auth_args
	
def alarm(ex, link = None):
	print(str(ex))
	time.sleep(60)
	if link is None:
		text = "EXCEPTION: " + str(ex)
	else:
		text = "EXCEPTION. Ошибка при отправке поста " + link + '\n\n' + str(ex)
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
			#post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется видосик: ' + item.title + ' ' + item.link
			post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется видосик: ' + create_href(item.link, item.title)
		elif item.type == 'audio':
			audios.append(item)
		elif item.type == 'gif':
			animations.append(item)
		elif item.type == 'doc':
			docs.append(item)
		elif item.type == 'link':
			post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, прикреплена ссылка: ' + create_href(item.link, item.title)
			#post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, прикреплена ссылка: [' + item.title + '](' + item.link + ')'		
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
	
	if len(animations) > 0:
		post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеются гифки\n'
		
	if len(docs) > 0:
		post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеются докУменты\n'
	
	last = 0 #id последнего сообщения, относящегося к посту
	try:
		if len(album) == 0:
			last = send_even_long_message(post.text)
		else:
			if len(post.text) < 1024:
				album[0].caption = post.text
				album[0].parse_mode = 'HTML'
			else:
				send_even_long_message(post.text)
			last = bot.send_media_group(my_id, album)[-1].message_id
		
		if len(animations) > 0:
			for gif in animations:
				last = bot.send_document(my_id, gif.link).message_id
			
		if len(docs) > 0:
			for doc in docs:
				last = bot.send_document(my_id, doc.link).message_id

	except Exception as e:
		alarm(e, create_href(post.link, post.source_name))
		
	try:
		bot.edit_message_reply_markup(my_id, last, reply_markup = create_markup(post.link[19:]))
	except Exception as e:
		bot.send_message(my_id, 'Проблемный пост, на те твои кнопки', reply_markup = create_markup(post.link[19:]))
	
def create_markup(data, liked = False):
	markup = InlineKeyboardMarkup()
	if not liked:
		markup.row(InlineKeyboardButton('Лайк', callback_data = 'ln' + data), InlineKeyboardButton('Pocket', callback_data = 'p' + data))
	else:
		markup.row(InlineKeyboardButton('Лайкнуто', callback_data = 'ly' + data), InlineKeyboardButton('Pocket', callback_data = 'p' + data))
	return markup
	
def send_even_long_message(text):
	while len(text) > 4096:
		bot.send_message(my_id, text[0:4096], parse_mode = 'HTML')
		text = text[4096:]
	return bot.send_message(my_id, text, parse_mode = 'HTML').message_id

handler_mode = ''
auth_args = [] #Лист аргументов для функции

apihelper.proxy = {'https':prox_ip} #Спасибо ркн
bot = telebot.TeleBot(token) 
print(bot.get_me()) #Проверка, что мы справились с ркн

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