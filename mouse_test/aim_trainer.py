# https://scratch.mit.edu/projects/694107194/editor/

import pyautogui
import time

color = (230, 200, 80)
tolerance = 50
def is_color(a) -> bool:
	return abs(a[0] - color[0]) < tolerance and abs(a[1] - color[1]) < tolerance and abs(a[2] - color[2]) < tolerance

def run() -> None:
	s = pyautogui.screenshot(imageFilename = r"my_screenshot.png") # grayscale=True
	for x in range(0, 1440, 5):
		for y in range(0, 900, 5):
			pix = s.getpixel((x * 2, y * 2))
			if is_color(pix):
				print("move")
				pyautogui.moveTo(x + 3, y + 3, .5)
				print("click")
				pyautogui.click(x + 3, y + 3)
				return

def main() -> None:
	time.sleep(5)
	pyautogui.click(1000, 500)
	for i in range(10):
		run()

# main()
time.sleep(2)
for i in range(100):

	pyautogui.click(650, 730)