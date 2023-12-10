import pyttsx3
import os
import json

engine = pyttsx3.init()


class Audiobook:
    active = None
    _tokens = list()

    def __init__(self, filepath=None):
        self.engine = engine #pyttsx3.init()
        # self.setup_engine()
        self.chapters = list()
        self.chapter_index = 0
        self.line_index = 0
        self.name = "unknown"
        self._location = 0  # location in the current text
        self.paused = True

        # ways to make this work from thread
        self.threaded = False
        self._need_update = False
        self.active = False
        self._done = False

        if filepath is not None:
            self.load(filepath)
            self.text = self._get_next_text()

    def setup_engine(self):
        if self is not Audiobook.active:
            if Audiobook.active is not None:
                Audiobook.active.pause()
                [engine.disconnect(token) for token in Audiobook._tokens]
            Audiobook.active = self
            tk1 = engine.connect("started-utterance", self.on_start_utterance)
            tk2 = engine.connect("started-word", self.on_word)
            tk3 = engine.connect("finished-utterance", self.on_end_utterance)
            Audiobook._tokens = [tk1, tk2, tk3]

    def put_chapters(self, chapters: list):
        self.chapters = chapters
        self.chapter_index = self.line_index = self._location = 0
        self.text = self._get_next_text()

    def _get_next_text(self):
        return self.chapters[self.chapter_index][self.line_index]

    def pause(self):
        self.paused = True
        # self.engine.stop()
        try:
            self.engine.endLoop()
        finally: pass

    def resume(self):
        self.setup_engine()
        if self.threaded:
            self.paused = False
            try:
                self.engine.startLoop(False)
                self.engine.say(self._get_next_text()[self._location:])
                self.engine.iterate()
            except: pass
        else:
            self.play()

    def skip_chapter(self, amount=1):
        self.line_index = 0
        self._location = 0
        self.chapter_index += amount
        self.text = self._get_next_text()
        self.apply_updates()

    def backup_chapter(self, amount=1):
        self.line_index = 0
        self._location = 0
        self.chapter_index -= amount
        self.text = self._get_next_text()
        self.apply_updates()

    def fast_forward(self, amount=100):
        self._location += amount
        if self._location >= len(self.text):
            self.on_end_utterance(self.name, True)
        self.apply_updates()

    def rewind(self, amount=100):
        self._location -= amount
        if self._location < 0:
            self._location = 0
        self.apply_updates()

    def save(self, name):
        base_path = "Audiobooks/" + name
        os.mkdir(base_path)
        with open(base_path+'/info.json', 'w') as file:  # configs
            json.dump({'name': name, 'rate': self.rate, 'voice': self.volume,
                       'chapter': self.chapter_index, 'line': self.line_index, 'location': self._location}
                      , file)
        for index, chapter in enumerate(self.chapters, start=1):
            filename = f"{base_path}/Chapter #{index}.txt"
            with open(filename, 'w') as file:
                for line in chapter:
                    file.write(line + '\n')

    def load(self, filename):
        files = os.listdir(filename)
        for file in sorted(files, key=lambda s: int(s[s.index('#')+1:s.index('.')]) if s.endswith('.txt') else 0):
            if file.endswith(".json"):
                self.settings = json.load(open(filename + '/' + file))
                self.name = os.path.basename(filename)
                self.rate = self.settings['rate']
                self.voice = self.settings['voice']
                self.chapter_index = self.settings['chapter']
                self.line_index = self.settings['line']
                self._location = self.settings['location']
            elif file.endswith(".txt"):
                lines = [line.strip() for line in open(filename + '/' + file)]
                self.chapters.append(lines)
            else:
                raise Exception("Unknown file loaded:", filename)
        self.text = self._get_next_text()

    def play(self):
        self.setup_engine()
        if self.threaded:
            self._play_threaded()
        else:
            self.paused = False
            while not self.paused:
                self.engine.say(self.text[self._location:], self.name)
                self.engine.runAndWait()

    def _play_threaded(self):
        self.paused = False
        self.engine.startLoop(False)
        self.engine.say(self._get_next_text()[self._location:], self.name)
        self.engine.iterate()

    # ------- callbacks ------- #
    def on_start_utterance(self, name):
        self._done = False
        print("reading chapter", self.chapter_index+1, self.line_index+1)

    def on_end_utterance(self, name, completed):
        if not completed: return  # todo: remove thing
        self._location = 0
        self.line_index += 1
        if self.line_index >= len(self.chapters[self.chapter_index]):
            self.line_index = 0
            self.chapter_index += 1
        self.text = self._get_next_text()
        self.engine.say(self.text, self.name)
        self._done = completed

    def on_word(self, name, location, length):
        self._location = location

    @staticmethod
    def utterance_error(name: str, exception: Exception):
        print(exception)

    # ------- parameters ------- #
    def apply_updates(self):
        if hasattr(self, 'text') and not self.paused:
            self.pause()
            self.resume()

    @property
    def rate(self):
        return self.engine.getProperty('rate')

    @rate.setter
    def rate(self, val):
        self.engine.setProperty('rate', val)
        self.apply_updates()

    @property
    def volume(self):
        return self.engine.getProperty('volume')

    @volume.setter
    def volume(self, val):
        self.engine.setProperty('volume', val)
        self.apply_updates()

    @property
    def voice(self):
        return self.engine.getProperty('voice')

    @voice.setter
    def voice(self, val):
        voices = self.engine.getProperty('voices')
        if isinstance(val, int):
            self.engine.setProperty('voice', voices[val].id)
        else:
            self.engine.setProperty('voice', val)
        self.apply_updates()

    @property
    @staticmethod
    def voices():
        return [v.name for v in engine.getProperty('voices')]

    def __repr__(self):
        return self.name


# engine.connect("started-utterance", Audiobook.active.on_start_utterance)
# engine.connect("started-word", Audiobook.active.on_word)
# engine.connect("finished-utterance", Audiobook.active.on_end_utterance)
engine.connect("error", Audiobook.utterance_error)

if __name__ == '__main__':
    pass