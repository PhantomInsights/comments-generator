"""
This script loads the contents of the specified .csv files and processes each comment
into the training model.
"""

import csv
import pickle

# The csv files you want to fit your training model..
CSV_FILES = ["username_1.csv",  "username_2.csv"]

# The subreddits comments you want to allow in the training model (lowercase). An empty list will allow all.
ALLOWED_SUBREDDITS = []

# How many leading words you need. 1 or 2 are the most common options.
ORDERS = 2


def init():
    """Reads the specified .csv file(s) and creates a training model from them.

    It is important to note that we merge all comments into a big string.
    This is to broaden the number of possibilities.
    """

    word_dictionary = dict()
    comments_list = list()

    for csv_file in CSV_FILES:

        # We iterate the .csv row by row.
        for row in csv.DictReader(open(csv_file, "r", encoding="utf-8")):

            if len(ALLOWED_SUBREDDITS) == 0:
                comments_list.append(row["body"])

            else:
                for subreddit in ALLOWED_SUBREDDITS:
                    if row["subreddit"] == subreddit:
                        comments_list.append(row["body"])
                        break

    # We separate each comment into words.
    words_list = " ".join(comments_list).split()

    for index, word in enumerate(words_list):

        # This will always fail in the last word since it doesn't have anything to pair it with.
        try:

            suffix = " ".join(words_list[index:index+ORDERS])
            prefix = words_list[index+ORDERS]

            # If the word is not in the dictionary, we init it with the next word.
            if word not in word_dictionary.keys():
                word_dictionary[suffix] = list([prefix])
            else:
                # Otherwise we append it to its inner list of possibilities.
                word_dictionary[suffix].append(prefix)

        except:
            pass

    # We name the pickle after the first element of the CSV_FILES list.
    with open("./{}.pickle".format(CSV_FILES[0].replace(".csv", "")), "wb") as model_file:
        pickle.dump(word_dictionary, model_file)


if __name__ == "__main__":

    init()
