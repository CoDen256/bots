import pyscreenshot as ImageGrab
import pyautogui
import time
from Xlib import display

def move(side):
	pyautogui.press(side, 2, 0.027)

def mouse_pos():
	print(pyautogui.position())


x = 517
y = 189
#218, 293, 363  = 70

def exist_branch(x, y):
	box = (x, y, x+1, y + 1 + 5 * 75) 
	im = ImageGrab.grab(box)
	rgb_im = im.convert('RGB')

	w, h = im.size
	#print(w,h)
	result = []
	for i in range(0,6):
		print(i*75)
		r, g, b = rgb_im.getpixel((0, h -1 - i * 75))
		summa = r + g + b
		if summa < 700:
			result.append(True)
		else:
			result.append(False)
		#print(y + h -1 - i * 75, result[-1])
	return result

def get_mouse():
	print([185 + i*75 for i in range(6)])
	while True:	
		data = display.Display().screen().root.query_pointer()._data
		x = data["root_x"]
		y = data["root_y"]
		print(str(x), str(y), exist_branch(x, y))

		time.sleep(1)

def main():
	start_x = 515
	start_y = 185

	while True:
		branches = exist_branch(start_x, start_y)
		
		cons_str = ""
		for elem in branches:
			if elem:
				cons_str += 'Left  '
			else:
				cons_str += 'Right '

		for elem in branches:
			if elem:
				move('left')
			else:
				move('right')
		time.sleep(0.024)

try:
	#get_mouse()
	time.sleep(5)
	main()
except Exception as e:
	print('Exit..')
	raise e