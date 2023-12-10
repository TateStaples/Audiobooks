import PySimpleGUI as gui
import library
from Audiobook import Audiobook, engine
import threading



class Window:
    theme = 'DarkAmber'

    def __init__(self):
        # <<, <, -, ⏯️, +, >, >>
        # book, voice, confirm
        gui.theme(self.theme)
        books = gui.OptionMenu(library.book_names, default_value=library.book_names[0])
        book = [gui.Text("Book"), books]
        adjust = [gui.Button(char) for char in ('<<', '<', '-', '⏯️', '+', '>', '>>')]
        voice = [gui.Text('Voices'), gui.OptionMenu([v.name for v in engine.getProperty('voices')])]
        self.layout = [
            adjust,
            book,
            voice + [gui.Button("Confirm")],
        ]
        self._inner = gui.Window("Audiobook Manager", self.layout, size =(300, 100))
        self.prev = None

    def start(self):
        window = self._inner
        while True:
            event, values = window.read()
            book_name, voice_name = values[0], values[1]
            book = library.get_book(book_name)
            if book is not self.prev:
                self.load_book(book)
            if event == "Confirm":
                book.voice = engine.setProperty('voice', voice_name)
            if book is None:
                pass
            elif event == '<<': book.backup_chapter()
            elif event == '<': book.rewind()
            elif event == '-': book.rate -= 50
            elif event == '+':
                book.rate = book.rate + 50
                print(book.rate)
            elif event == '>': book.fast_forward()
            elif event == '>>': book.skip_chapter()
            elif event == '⏯️':
                if book.active:
                    if book.paused:
                        book.resume()
                    else:
                        book.pause()
                else:
                    book.active = True
                    book.play()
                    # t = threading.Thread(target=book.play)
                    # t.start()
            elif event == gui.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
                print('quitting')
                break
        self.quit()


    def load_book(self, book):
        book.threaded = True
        if self.prev is not None:
            book.rate = self.prev.rate
            book.voice = self.prev.voice
            self.prev.active = False
            self.prev.pause()
        book = self.prev

    def quit(self):
        print('so long')
        self._inner.close()
        quit()


if __name__ == '__main__':
    # threading.Thread(target=Window().start).start()
    Window().start()
    print('here')
    while True: pass