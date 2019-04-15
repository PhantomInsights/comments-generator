"""
A script that generates sentences using markov chains.
"""

import pickle
import random

import config

MODEL_FILE = "./model.pickle"


def init():
    """Inits the bot by fetching the inbox and replying with newly generated comments."""

    # Load the model.
    model = read_model(MODEL_FILE)
    model_keys = list(model.keys())

    new_comment = generate_comment(model=model, order=2,
                                   number_of_sentences=2,
                                   initial_prefix=get_prefix(model))

    print(new_comment)


def read_model(file_name):
    """Loads the specified pickle file.

    Parameters
    ----------
    file_name : str
        The location the pickle file.

    Returns
    -------
    dict
        The dictionary inside the pickle.

    """

    with open(file_name, "rb") as model_file:
        return pickle.load(model_file)


def get_prefix(model):
    """Get a random prefix that starts in uppercase.

    Parameters
    ----------
    model : dict
        The dictionary containing all the pairs and their possible outcomes.

    Returns
    -------
    str
        The randomly selected prefix.

    """

    model_keys = list(model.keys())

    # We give it a maximum of 10,000 tries.
    for _ in range(10000):

        random_prefix = random.choice(model_keys)

        if random_prefix[0].isupper():

            ends_with_punctuation = False
            stripped_suffix = random_prefix.strip()

            for char in [".", "?", "!"]:
                if stripped_suffix[-1] == char:
                    ends_with_punctuation = True
                    break

            if not ends_with_punctuation:
                break

    return random_prefix


def generate_comment(model, number_of_sentences, initial_prefix, order):
    """Generates a new comment using the model and an initial prefix.

    Parameters
    ----------
    model : dict
        The dictionary containing all the pairs and their possible outcomes.

    number_of_Sentences : int
        The maximum number of sentences.

    initial_prefix : str
        The word(s) that will start the chain.

    order : int
        The number of words in the state, this must match the order number in step2.py

    Returns
    -------
    str
        The newly generated text.

    """

    counter = 0
    latest_suffix = initial_prefix
    final_sentence = latest_suffix + " "

    # We add a maximum sentence length to avoid going infinite in edge cases.
    for _ in range(500):

        try:
            latest_suffix = random.choice(model[latest_suffix])
        except:
            # If we don't get another word we take another one randomly and continue the chain.
            latest_suffix = get_prefix(model)

        final_sentence += latest_suffix + " "
        latest_suffix = " ".join(final_sentence.split()[-order:]).strip()

        for char in [".", "?", "!"]:
            if latest_suffix[-1] == char:
                counter += 1
                break

        if counter >= number_of_sentences:
            break

    return final_sentence


if __name__ == "__main__":

    init()
