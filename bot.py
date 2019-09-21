import telebot
import os

from telebot import apihelper
from config import token, prox_ip, my_id
from telebot.types import InputMediaPhoto, InputMediaVideo, InputMediaAnimation, InputMediaAudio, InputMediaDocument

def two_fact():	#Ввод кода двухфакторной аутентификации в чате бота
	auth_args = [] #Лист аргументов для функции

	@bot.message_handler(content_types=['text']) #Штука, которая примет код
	def get_auth_code_from_message(message):
		if message.from_user.id == my_id:
			auth_args.append(message.text)
			bot.delete_message(my_id, message.message_id)
			bot.stop_polling() #Выключаем ожидание

	bot.send_message(my_id, 'СЛЫШ ВВОДИ') #Приглашаем пользователя (меня) ввести код
	
	bot.polling() #Ожидаем
	
	bot.send_message(my_id, 'ПРИНЯТО')
	auth_args.append(False) #Второй аргумент
	return auth_args

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
		elif item.type == 'poll':
			post.text += '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется ' + item.link
		elif item.type == 'wiki':
			post.text +='\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеется вики-страница: ' + create_href(item.link, item.title)
			
	if len(audios) > 0:
		post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеются аудио:\n'
		for audio in audios:
			post.text = post.text + audio.author + ' - ' + audio.title
	
	if len(animations) > 0:
		post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеются гифки\n'
		
	if len(docs) > 0:
		post.text = post.text + '\n\nАНТОН, ОБРАТИ ВНИМАНИЕ, имеются докУменты\n'
	
	if len(album) == 0:
		bot.send_message(my_id, post.text, parse_mode = 'HTML')
	else:
		if len(post.text) < 1024:
			album[0].caption = post.text
			album[0].parse_mode = 'HTML'
		else:
			bot.send_message(my_id, post.text, parse_mode = 'HTML')
		bot.send_media_group(my_id, album)
	
	if len(animations) > 0:
		for gif in animations:
			bot.send_animation(my_id, gif.link)
			
	if len(docs) > 0:
		for doc in docs:
			bot.send_document(my_id, doc.link)
	
apihelper.proxy = {'https':prox_ip} #Спасибо ркн
bot = telebot.TeleBot(token) 
print(bot.get_me()) #Проверка, что мы справились с ркн

def create_href(link, text):
	return '<a href=\"' + link + '\">' + text + '</a>'	

def check_down():
	@bot.message_handler(content_types=['text'])
	def is_down(message):
		if (message.text.lower().find('упал') != -1) and (message.text[-1] == '?'):
			bot.send_message(my_id, 'Не упал')
		elif message.text.lower().find('падай') != 1:
			bot.send_photo(my_id, 'https://pbs.twimg.com/media/DwVI7QBWkAEsY1g.jpg')
			os._exit(0)

	bot.polling()

#updates = bot.get_updates()
#print(updates[0].message.from_user.id)

#bot.send_message(my_id, 'дарова')

#album = []
#album.append(InputMediaPhoto('https://sun9-62.userapi.com/c855324/v855324525/f1855/wnRgTdrHv7E.jpg', 'привет'))
#album.append(InputMediaPhoto('https://sun9-62.userapi.com/c855324/v855324525/f1855/wnRgTdrHv7E.jpg'))

#bot.send_photo(my_id, 'https://sun9-62.userapi.com/c855324/v855324525/f1855/wnRgTdrHv7E.jpg', 'привет дворяне')
#bot.send_media_group(my_id, album);
