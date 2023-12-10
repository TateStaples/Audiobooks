from Audiobook import Audiobook

audiobook = Audiobook()
search_string = ''
first = False

for c_i, chapter in enumerate(audiobook.chapters, start=1):
    for l_i, line in enumerate(chapter, start=1):
        if search_string in line:
            print(f"found in chapter {c_i}, line #{l_i}")


if __name__ == '__main__':
    pass

