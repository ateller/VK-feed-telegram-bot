import vk_api
import pprint
from config import login, passw, ignore #Должен быть файл config.py, в нем логин, пароль от вк, список слов для игнора, токен бота, id чата, куда все скидывать и айпи прокси
from bot import two_fact, send_post, check_down, create_href
from threading import Thread
import time
import datetime

class post:
	def __init__(self, dict_post, i):
		self.text = find_group_name(dict_post['groups'], dict_post['items'][i]['source_id']) + ' '
		self.text += create_href(create_link(dict_post['items'][i]['post_id'], dict_post['items'][i]['source_id']), 'пишетъ')
		self.text += ':\n\n'
		self.text += dict_post['items'][i]['text']
		
		self.media = []
		if 'attachments' in dict_post['items'][i]:
			for attachment in dict_post['items'][i]['attachments']:
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
						self.media.append(media('', 'playlist', title = attachment['link']['title']))
					else:
						self.media.append(media(attachment['link']['url'], 'link', title = attachment['link']['title']))
				elif attachment['type'] == 'poll':
					poll = media('', 'poll')
					if attachment['poll']['anonymous']:
						poll.link = 'анонимный опросик \"'
					else:
						poll.link = 'публичный опросик \"'
					
					#Извиняюсь за то, что просто сую весь текст в линк
					
					poll.link += attachment['poll']['question'] + '\". Проголосовало ' + attachment['poll']['votes'] + ' человек:\n'
					
					for answ in attachment['poll']['answers']:
						poll.link += '\t - ' + answ['text'] + ' - ' + answ['votes'] + '\n'
					
					if attachment['poll']['closed']:
						poll.link += 'Опрос завершен'
					elif attachment['poll']['multiple']:
						poll.link += 'Можно выбрать несколько вариантов ответа до'
					else: 
						poll.link += 'Можно выбрать oдин вариант ответа'
						
					t = attachment['poll']['end_date']
					
					if t != 0:
						poll.link += ' до ' + utc_3(datetime.fromtimestamp(t)).strftime('%H:%M %d.%m.%Y')
					
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
		
def create_link(post_id, group_id):
	link = 'https://vk.com/wall' + str(group_id) + '_' + str(post_id) #Делаем ссылку на группу
	return link
	
def utc_3(dt):
	dt.hour += 3
	return dt

def handle_dict(dict):
	global start
	count = len(dict['items'])
	if count > 0:
		start = dict['items'][0]['date'] + 1 #Потом будем запрашивать посты со следующей секунды после последнего поста в этой пачке
		while count > 0:
			if not check_ignore(dict['items'][count - 1]['text']):
				send_post(post(dict, count - 1))
			count -= 1
		
def check_ignore(text):
	for i in ignore:
		if text.find(i) != -1:
			return True
	return False
#Список слов, которые я не хочу видеть у себя в ленте
	
def find_group_name(groups, id):
	for group in groups:
		if group['id'] == -id:
			return group['name']
#В списке групп ищем ту, у которой нужный id
			
def check_wall():
	while True:
		handle_dict(vk.newsfeed.get(filters = 'post', return_banned = 0, start_time = start))
		time.sleep(1)
#Раз в секунду просим новые посты
	
vk_session = vk_api.VkApi(login, passw, auth_handler = two_fact)
vk_session.auth()
#Создаем сессию

vk = vk_session.get_api() #Получаем доступ к методам

pprint.pprint(vk.newsfeed.get(filters = 'post', return_banned = 0, start_time = 1568572461, count = 1)) #Печатаем в терминал последнюю запись. Просто чтобы была

start = 1568572461 #Рандомное время
handle_dict(vk.newsfeed.get(filters = 'post', return_banned = 0, start_time = start, count = 1)) #Прогоняем последнюю, чтобы время установилось

thread1 = Thread(target=check_wall) #Пересылка записей
thread2 = Thread(target=check_down, daemon=True) #Можно проверять из чата, работает ли бот

thread1.start()
thread2.start()
thread1.join() #Если вылетает первый поток, он присоединяется и скрипт завершается, а первый демон

#check_wall()

#start = vk.newsfeed.get(filters = 'post', return_banned = 0, start_time = 1568572461, count = 1)['next_from']

#send_post(get_post)