"""
This script loads the contents of the specified .txt files and processes their contents
into the training model.
"""

import csv
import pickle

RESULT_FILE = "model.pickle"

# The txt files you want to fit your training model.
TXT_FILES = ["file1.txt", "file2.txt"]

# The order (memory length in words) you need. 1 or 2 are the most common options.
ORDER = 2


def init():
    """Reads the specified .txt file(s) and creates a training model from them.   
    It is important to note that we merge all texts into a big string.
    This is to broaden the number of outcomes.
    """

    word_dictionary = dict()
    texts_list = list()

    for txt_file in TXT_FILES:

        with open(txt_file, "r", encoding="utf-8") as temp_file:
            file_text = temp_file.read()
            texts_list.append(file_text)

    # We separate each comment into words.
    words_list = " ".join(texts_list).split()

    for index, _ in enumerate(words_list):

        # This will always fail in the last word since it doesn't have anything to pair it with.
        try:
            prefix = " ".join(words_list[index:index+ORDER])
            suffix = words_list[index+ORDER]

            # If the word is not in the dictionary, we init it with the next word.
            if prefix not in word_dictionary.keys():
                word_dictionary[prefix] = list([suffix])
            else:
                # Otherwise we append it to its inner list of outcomes.
                word_dictionary[prefix].append(suffix)
        except:
            pass

    # We save the dict as a pickle so we can reuse it on other scripts.
    with open("./{}".format(RESULT_FILE), "wb") as model_file:
        pickle.dump(word_dictionary, model_file)


if __name__ == "__main__":

    init()
