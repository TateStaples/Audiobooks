from Audiobook import Audiobook
import os

base_path = "Audiobooks/"
books = [Audiobook(base_path+name) for name in os.listdir(base_path)]
book_names = [book.name for book in books]


def get_book(name):
    return books[book_names.index(name)]