import pyautogui
import time
i=0
while i<10:
    pyautogui.moveRel(0,10)
    i+=1
    time.sleep(1)