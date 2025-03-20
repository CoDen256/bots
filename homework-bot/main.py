import config
from localization import local
from data import grouped, subject_list, full_names
from classes import *

bot = Bot(config.token)

bot.homeworks = config.init_homeworks(bot)

ids = [283382228, 415631776]

for id in ids:
	bot.selected[id] = [None]


### launching and finishing handlers ###

@bot.message_handler(commands=["stop", 'exit'])
def stop(message):
    print('Exiting...')
    bot.stop_polling()


@bot.message_handler(commands=['start', 'help'])
def start(message):
	if not message.chat.id in bot.selected: # adding id to the homeworks id
		bot.selected[message.chat.id] = [None]
		print(message.chat.id)

	bot.create_markup('start', [('/select', '/stop')])

	bot.send(message, local['start'])





### /select chain ###

@bot.message_handler(commands=['select'])
def select(message):
	id = message.chat.id

	bot.adding = 0
	bot.selected[id] = None
	bot.selection = True

	bot.create_markup('full names', full_names)

	request = message.text.split('/select')[1].strip() # taking [subject] from /select [subject]

	if request:
		define_subject(message) # /select [subject]
	else:
		bot.send(message, local['select'])


@bot.message_handler(func = lambda m : not bot.selected[m.chat.id] and bot.selection)
def define_subject(message):
	id = message.chat.id
	bot.create_markup('full names')

	chosen = message.text.split('/select')[-1].strip()
	chosen_l = chosen.lower()
	

	if chosen_l not in subject_list:
		bot.send(message, local['invalid subject'])

	else:
		bot.selected[id] = bot.homeworks[subject_list[chosen_l]] #id : [hw1, (hw2)]

		bot.send(message, local['chosen']+chosen)

		if len(bot.selected[id]) == 2: # if is grouped

			bot.create_markup('groups', [('1', '2')])
			bot.send(message, local['group'])

		elif len(bot.selected[id]) == 1: # if not grouped

			bot.create_markup('selected', [('/add','/delete'),('/select', '/homework')])
			
			bot.send(message, local['selected'])

			bot.selection = False
			#bot.selected[id] = bot.selected[id][0] # id:homework object
	
		else:
			print('unable to add new homework')
			print(len(bot.selected[id]))
			#bot.create_markup('add homework', (['/add']))
			#bot.send(message, local['no homework'])
#
			#bot.selection = False
#
			#bot.selected[id] = [Homework(subject_list[chosen_l], '', '', '', '')]

@bot.message_handler(func = lambda m: len(bot.selected[m.chat.id]) == 2 and bot.selection)
def define_group(message):
	id = message.chat.id
	gr = message.text

	if gr == '1' or gr == '2':
		bot.selection = False

		for grouped_hw in bot.selected[id]: # choosing appropriate group

			if int(grouped_hw.group) == int(gr):

				bot.selected[id] = [grouped_hw]


		bot.create_markup('selected', [('/add','/delete'),('/select', '/homework')])

		bot.send(message, gr + local['group selected'])
		bot.send(message, local['selected'])

	else:
		bot.send(message, local['group invalid'])

# after this chain bot.selected looks like this {id1:[hw], id2:[hw]}

@bot.message_handler(func=lambda m: not bot.selection and bot.selected[m.chat.id][0], commands=['homework'])
def show(message):
	id = message.chat.id

	current = bot.selected[id][0]

	if not current.topic:
		bot.create_markup('/add')
		bot.send(message, local['no homework'])
	else:
		info = ''
		info += local['show_subject'] +  current.subject + '\n'
		info += local['show_topic'] +  current.topic + '\n'
		info += local['show_task'] +  current.content + '\n'
		info += local['show_deadline'] + config.dt_format(current.date) +  '\n'
		if current.additional:
			info += local['show_additional'] +  current.additional + '\n'

		bot.send(message, local['show_hw'])
		bot.send(message, info)

		if current.photo:
			if current.photo[0] == 'p': # 'type+file_id'
				bot.photo(message, current.photo[1:])
			elif current.photo[0] == 'd': # document
				bot.document(message, current.photo[1:])

### ADD SECTION ###

@bot.message_handler(func=lambda m: not bot.selection and bot.selected[m.chat.id][0], commands=['add'])
def add(message):
	id = message.chat.id

	bot.delete_markup()

	bot.new_hw = {'subject':bot.selected[id][0].subject, 'group':bot.selected[id][0].group} # through funcs will be added new info and then created new Hw object
	bot.adding += 1
	bot.send(message, local['adding_topic'])

@bot.message_handler(func=lambda m: not bot.selection and bot.selected[m.chat.id][0] and bot.adding == 1) # topic
def add_topic(message):

	bot.new_hw['topic'] = message.text

	bot.adding += 1
	bot.send(message, local['adding_task'])


@bot.message_handler(func=lambda m: not bot.selection and bot.selected[m.chat.id][0] and bot.adding == 2) # content
def add_content(message):

	bot.new_hw['content'] = message.text

	bot.adding += 1
	bot.send(message, local['adding_deadline'])


@bot.message_handler(func=lambda m: not bot.selection and bot.selected[m.chat.id][0] and bot.adding == 3) # date
def add_date(message):

	bot.new_hw['date'] = message.text

	bot.adding += 1
	bot.send(message, local['adding_photo'])


@bot.message_handler(func=lambda m: not bot.selection and bot.selected[m.chat.id][0] and bot.adding == 4, content_types=['text']) # text instead of photo
def add_photo(message):
	bot.new_hw['photo'] = ''

	bot.adding += 1
	bot.send(message, local['adding_additional'])


@bot.message_handler(func=lambda m: not bot.selection and bot.selected[m.chat.id][0] and bot.adding == 4, content_types=['photo']) # photo 
def add_photo(message):

	bot.new_hw['photo'] = 'p'+message.photo[0].file_id

	bot.adding += 1
	bot.send(message, local['adding_additional'])

@bot.message_handler(func=lambda m: not bot.selection and bot.selected[m.chat.id][0] and bot.adding == 4, content_types=['document']) # document 
def add_photo(message):

	bot.new_hw['photo'] = 'd'+message.document.file_id

	bot.adding += 1
	bot.send(message, local['adding_additional'])

@bot.message_handler(func=lambda m: not bot.selection and bot.selected[m.chat.id][0] and bot.adding == 5) # additional
def add_additional(message):

	bot.create_markup('added', [['/select']])

	bot.new_hw['additional'] = message.text if message.text.lower() not in ['no', '-', 'нет', 'не', "ні", 'no'] else ''
 
	new_homework = config.generate_hw(bot.new_hw) # => homework object

	config.add_homework(new_homework, bot, message.chat.id)

	bot.adding = 0
	bot.send(message, local['added'])




### DELETE ###
@bot.message_handler(func=lambda m: not bot.selection and bot.selected[m.chat.id][0], commands=['delete'])
def delete(message):
	bot.create_markup('added', ['/select'])
	bot.send(message, bot.selected[message.chat.id][0].subject + local['deleted'])
	config.delete_homework(bot.selected[message.chat.id][0], bot, message.chat.id)



### Non-scripted handlers ###

@bot.message_handler(content_types=['text'])
def nonscript(message):
	print(bot.adding)
	bot.send(message, local['nonscript'])

@bot.message_handler(content_types=["sticker", "pinned_message", "photo", "audio"])
def nontext(message):
	bot.send(message, local['nontext'])


bot.polling(none_stop=True)
