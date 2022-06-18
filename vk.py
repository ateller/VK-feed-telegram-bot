import vk_api
from config import ignore, my_id #Должен быть файл config.py, в нем список слов для игнора, токен бота, id чата, куда все скидывать и ключ и токен от покета
from bot import bot, two_fact, cap_handl, send_post, check_down, create_href, get_log_pass, alarm, create_markup, fix_html
from threading import Thread
from getpocket import p

import time
import datetime
import re

class post:
	def __init__(self, groups, profiles, dict_post, repost = False):
		self.text = ''
		
		if repost == True:
			self.text += 'ПОСТ ВЫШЕ - РЕПОСТ ЭТОГО ПОСТА\n\n'
			self.source_name = find_name(groups, profiles, dict_post['from_id'])
			self.link = create_link(dict_post['id'], dict_post['from_id'])
		else:
			self.source_name = find_name(groups, profiles, dict_post['source_id'])
			self.link = create_link(dict_post['post_id'], dict_post['source_id'])
		
		self.source_name = fix_html(self.source_name)
		self.text += self.source_name + ' '
		self.text += create_href(self.link, 'пишетъ')
		
		self.text += ':\n\n'
		self.text += replace_vk_hidden_links(fix_html(dict_post['text']))
		
		self.media = []
		if 'attachments' in dict_post:
			for attachment in dict_post['attachments']:
				if attachment['type'] == 'photo':
					link = ''
					max_size = 0
					for size in attachment['photo']['sizes']:
						if size['height'] > max_size:
							max_size = size['height']
							link = size['url']
						if size['width'] > max_size:
							max_size = size['width']
							link = size['url']
					self.media.append(media(link, 'photo'))
				elif attachment['type'] == 'video':
					link = 'https://vk.com/video' + str(attachment['video']['owner_id']) + '_' + str(attachment['video']['id'])
					self.media.append(media(link, 'video', title = attachment['video']['title']))
				elif attachment['type'] == 'audio':
					self.media.append(media(attachment['audio']['url'], 'audio', title = attachment['audio']['title'], author = attachment['audio']['artist']))
				elif attachment['type'] == 'doc':
					if attachment['doc']['type'] == 3:
						self.media.append(media(attachment['doc']['url'], 'gif'))
					else:
						self.media.append(media(attachment['doc']['url'], 'doc', title = attachment['doc']['title']))
				elif attachment['type'] == 'link':
					if attachment['link']['description'] == 'Плейлист':
						self.media.append(media(attachment['link']['url'], 'playlist', title = attachment['link']['title']))
					else:
						self.media.append(media(attachment['link']['url'], 'link', title = attachment['link']['title']))
				elif attachment['type'] == 'poll':
					poll = media('', 'poll')
					if attachment['poll']['anonymous']:
						poll.link = 'анонимный опросик \"'
					else:
						poll.link = 'публичный опросик \"'
					
					#Извиняюсь за то, что просто сую весь текст в линк
					
					poll.link += attachment['poll']['question'] + '\". Проголосовало ' + str(attachment['poll']['votes']) + ' человек:\n'
					
					for answ in attachment['poll']['answers']:
						poll.link += '\t - ' + answ['text'] + ' - ' + str(answ['votes']) + '\n'
					
					if attachment['poll']['closed']:
						poll.link += 'Опрос завершен'
					elif attachment['poll']['multiple']:
						poll.link += 'Можно выбрать несколько вариантов ответа'
					else: 
						poll.link += 'Можно выбрать oдин вариант ответа'
						
					t = attachment['poll']['end_date']
					
					if t != 0:
						poll.link += ' до ' + utc_3(datetime.datetime.fromtimestamp(t)).strftime('%H:%M %d.%m.%Y')
					
					self.media.append(poll)
					
				elif attachment['type'] == 'page':
					self.media.append(media(attachment['page']['view_url'], 'wiki', title = attachment['page']['title']))
				elif attachment['type'] == 'album':
					self.media.append(media('', 'album', title = attachment['album']['title']))
				elif attachment['type'] == 'market':
					self.media.append(media('', 'market', title = attachment['market']['title']))
				elif attachment['type'] == 'market_album':
					self.media.append(media('', 'market_album', title = attachment['market_album']['title'] + ' из ' + str(attachment['market_album']['count'])))
				elif attachment['type'] == 'event':
					self.media.append(media('', 'event', title = attachment['event']['text'] + ' в ' + attachment['event']['address'] + ' в ' + utc_3(datetime.fromtimestamp(attachment['event']['time'])).strftime('%H:%M %d.%m.%Y') + ' по московскому времени'))
					
class media:
	def __init__(self, link, type, title = '', author = ''):
		self.link = link
		self.type = type
		self.title = title
		self.author = author
		
@bot.callback_query_handler(func = lambda call: True)
def button_handler(call):
	if call.from_user.id == my_id:
		try:
			if call.data[0] == 'l':
				ids = call.data[2:].split('_')
				source_id = int(ids[0])
				post_id = int(ids[1])
				if vk.likes.isLiked(type = 'post', owner_id = source_id, item_id = post_id)['liked'] == 0:	#Если запись не лайкнута
					if call.data[1] == 'n':																	#И кнопка соотвествует
						vk.likes.add(type = 'post', owner_id = source_id, item_id = post_id)				#То лайкаем, и меняем кнопку
						bot.edit_message_reply_markup(my_id, call.message.message_id, reply_markup = create_markup(call.data[2:], liked = 1))
						bot.answer_callback_query(call.id, 'Лайкнуто')
					elif call.data[1] == 'y':																#А если кнопка лжет, приводим кнопку в соответствие и уведомляем. Ниже аналогично
						bot.edit_message_reply_markup(my_id, call.message.message_id, reply_markup = create_markup(call.data[2:], liked = 0))
						bot.answer_callback_query(call.id, 'А ты уже убрал лайк в вк, лол')
					elif call.data[1] == 'd':
						bot.answer_callback_query(call.id, 'Потерли пост, всё уже')
				else:
					if call.data[1] == 'y':
						vk.likes.delete(type = 'post', owner_id = source_id, item_id = post_id)
						bot.edit_message_reply_markup(my_id, call.message.message_id, reply_markup = create_markup(call.data[2:], liked = 0))
						bot.answer_callback_query(call.id, 'Лайк убран')
					elif call.data[1] == 'n':
						bot.edit_message_reply_markup(my_id, call.message.message_id, reply_markup = create_markup(call.data[2:], liked = 1))
						bot.answer_callback_query(call.id, 'А ты уже лайкнул в вк, лол')
			elif call.data[0] == 'p':
				p.add('https://vk.com/wall' + call.data[1:])
				bot.answer_callback_query(call.id, 'Добавлено в покет')
		except Exception as e:
			if '[100] One of the parameters specified was missing or invalid: object not found' in str(e):
				bot.edit_message_reply_markup(my_id, call.message.message_id, reply_markup = create_markup(call.data[2:], liked = 2))
				bot.answer_callback_query(call.id, 'Опа, а пост потерли')
			else:
				alarm(e)

def create_link(post_id, group_id):
	link = 'https://vk.com/wall' + str(group_id) + '_' + str(post_id) #Делаем ссылку на группу
	return link
	
def replace_vk_hidden_links(text):
	parsed = re.findall(r'\[.*?\|.*?\]', text)
	parsed = set(parsed)
	for item in parsed:
		splited = item.split('|')
		text = text.replace(item, create_href('https://vk.com/' + splited[0][1:], splited[1][:-1]))
	return text
	
def utc_3(dt):
	return dt + datetime.timedelta(hours = 3)

def handle_dict(dict):
	global start
	count = len(dict['items'])
	if count > 0:
		start = dict['items'][0]['date'] + 1 #Потом будем запрашивать посты со следующей секунды после последнего поста в этой пачке
		while count > 0:
			temp = dict['items'][count - 1] #Текущий пост
			if not check_ignore(temp['text']): #Проверяем игнор лист
				send_post(post(dict['groups'], dict['profiles'], temp)) #Шлем пост
				if 'copy_history' in temp: #Если это репост, то шлем всю историю репостов
					for repost in temp['copy_history']:
						send_post(post(dict['groups'], dict['profiles'], repost, repost = True))
			count -= 1
		
def check_ignore(text):
	for i in ignore:
		if i in text:
			return True
	return False
#Список слов, которые я не хочу видеть у себя в ленте
	
def find_name(groups, profiles, id):
	for group in groups:
		if group['id'] == -id:
			return group['name']
	#В списке групп ищем ту, у которой нужный id
	for user in profiles:
		if user['id'] == id:
			return user['first_name'] + ' ' + user['last_name']
	#Если не нашли, это человеческий пост, ищем человека

			
def check_wall():
	while True:
		try:
			handle_dict(vk.newsfeed.get(filters = 'post', return_banned = 0, start_time = start))
		except Exception as e:
			alarm(e)
			handle_dict(vk.newsfeed.get(filters = 'post', return_banned = 0, start_time = start))
		time.sleep(10)
#Раз в десять сек просим новые посты

log_pass = get_log_pass()
vk_session = vk_api.VkApi(log_pass[0], log_pass[1], auth_handler = two_fact, captcha_handler = cap_handl)

vk_session.auth()
#Создаем сессию

vk = vk_session.get_api() #Получаем доступ к методам

start = 1568572461 #Рандомное время
handle_dict(vk.newsfeed.get(filters = 'post', return_banned = 0, start_time = start, count = 1)) #Прогоняем последнюю, чтобы время установилось

thread1 = Thread(target=check_wall) #Пересылка записей
thread2 = Thread(target=check_down, daemon=True) #Можно проверять из чата, работает ли бот

thread1.start()
thread2.start()
thread1.join() #Если вылетает первый поток, он присоединяется и скрипт завершается, а второй демон