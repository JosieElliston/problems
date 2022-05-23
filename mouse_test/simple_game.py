# https://scratch.mit.edu/projects/694107194/editor/

import pyautogui
import time
left = 220
top = 140
right = 1230
bottom = 870
width = right - left
height = bottom - top



color = (0, 0, 0, 255)
def is_color(a) -> bool:
	return abs(a[0] - color[0]) < 10 and abs(a[1] - color[1]) < 10 and abs(a[2] - color[2]) < 10

def run() -> None:
	s = pyautogui.screenshot(imageFilename = r"my_screenshot.png") # grayscale=True
	for x in range(left, right, 110):
		for y in range(top, bottom, 110):
			if color == s.getpixel((x * 2, y * 2)):
				pyautogui.click(x + 10, y + 10)
				return
	raise ValueError

def main() -> None:
	time.sleep(1)
	for i in range(20):
		run()

main()
