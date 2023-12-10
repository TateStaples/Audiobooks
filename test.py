from Audiobook import Audiobook
import threading, time


a = Audiobook()

a.text = "hello world"

def test(*args):
    a.play()


for i in range(3):
    t = threading.Thread(target=test)
    t.start()
    time.sleep(0.2)