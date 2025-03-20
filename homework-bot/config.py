from classes import Homework, SQLighter

token = ''


def init_homeworks(bot):

	short_names = ['OP', 'LA', 'MA', 'EN', 'HU', 'DM', 'OOS']
	grouped = ['EN']
	pattern = {key:[] for key in short_names}

	session = SQLighter('homework.db')

	db = session.select_all()

	session.close()

	for row in db:
		new_hw = Homework(*row)

		try:

			pattern[new_hw.subject].append(new_hw)
		except KeyError as e:
			print('Warning!', new_hw.subject)
			print('Such a subject doesn\'t exsist.\nIt wasn\'t initialized.')

	for key in pattern:
		if not pattern[key]:
			if key in grouped:
				pattern[key] = [Homework(key, '', '', '', '1'), Homework(key, '', '', '', '2')]
			else:
				pattern[key] = [Homework(key, '', '', '', '-1')]

		if len(pattern[key]) == 1 and key in grouped:
			if pattern[key][0].group == 1:
				pattern[key].append(Homework(key, '', '', '', '2'))
			else:
				pattern[key].append(Homework(key, '', '', '', '1'))

	return pattern

def delete_homework(homework, bot, id):
	session = SQLighter('homework.db')

	db = session.delete(homework)

	session.close()

	bot.homeworks = init_homeworks(bot)
	bot.selected[id] = [None] # no selected homework for current user

def add_homework(homework, bot, id):
	

	for hw in bot.homeworks[homework.subject]:
		if hw.group == homework.group:
			print('Deleting', hw.subject, hw.topic)
			delete_homework(hw, bot, id)

	session = SQLighter('homework.db')
	db = session.add(homework)

	session.close()

	bot.homeworks = init_homeworks(bot)

def wipe_homeworks(total):
	for key in total:
		for homework in total[key]:
			session = SQLighter('homework.db')

			db = session.delete(homework)

			session.close()

def dt_format(datetime):
	return datetime

def generate_hw(d):
	return Homework(d['subject'],d['topic'],d['content'],d['date'],d['group'],d['photo'],d['additional'])