"""
This script loads the contents of the specified .csv files and processes each comment
into the training model.
"""

import csv
import pickle

RESULT_FILE = "model.pickle"

# The csv files you want to fit your training model.
CSV_FILES = ["username_1.csv", "username_2.csv"]

# The subreddits comments you want to allow in the training model (lowercase). An empty list will allow all.
ALLOWED_SUBREDDITS = []

# The order (memory length in words) you need. 1 or 2 are the most common options.
ORDER = 2


def init():
    """Reads the specified .csv file(s) and creates a training model from them.   
    It is important to note that we merge all comments into a big string.
    This is to broaden the number of outcomes.
    """

    word_dictionary = dict()
    comments_list = list()

    for csv_file in CSV_FILES:

        # We iterate the .csv row by row.
        for row in csv.DictReader(open(csv_file, "r", encoding="utf-8")):

            # We skip empty comments.
            if len(row["body"]) == 0:
                continue

            # Remove unnecessary whitespaces.
            row["body"] = row["body"].strip()

            # To improve results we ensure all comments end with a period.
            ends_with_punctuation = False

            for char in [".", "?", "!"]:

                if row["body"][-1] == char:
                    ends_with_punctuation = True
                    break

            if not ends_with_punctuation:
                row["body"] = row["body"] + "."

            if len(ALLOWED_SUBREDDITS) == 0:
                comments_list.append(row["body"])

            else:
                # We check if the subreddit comment is in our allowed subreddits list.
                if row["subreddit"].lower() in ALLOWED_SUBREDDITS:
                    comments_list.append(row["body"])

    # We separate each comment into words.
    words_list = " ".join(comments_list).split()

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

    # We save the dict as a pickle so we can reuse it on the bot script.
    with open("./{}".format(RESULT_FILE), "wb") as model_file:
        pickle.dump(word_dictionary, model_file)


if __name__ == "__main__":

    init()
