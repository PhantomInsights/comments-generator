"""
A Reddit bot that replies to unread messages with newly generated markov chains.
"""

import pickle
import random

import praw
import config

MODEL_FILE = "./model.pickle"
COMMENTS_LOG = "./processed_comments.txt"

# These users will be ignored to avoid errors and infinite replies.
IGNORED_USERS = ["reddit", "AutoModerator", None]

# The stop words files.
ES_STOPWORDS_FILE = "./assets/stopwords-es.txt"
EN_STOPWORDS_FILE = "./assets/stopwords-en.txt"

STOP_WORDS = set()


def add_extra_words():
    """Adds the title and uppercase version of all words to STOP_WORDS.

    We parse local copies of stop words downloaded from the following repositories:

    https://github.com/stopwords-iso/stopwords-es
    https://github.com/stopwords-iso/stopwords-en
    """

    with open(ES_STOPWORDS_FILE, "r", encoding="utf-8") as temp_file:
        for word in temp_file.read().splitlines():
            STOP_WORDS.add(word)

    with open(EN_STOPWORDS_FILE, "r", encoding="utf-8") as temp_file:
        for word in temp_file.read().splitlines():
            STOP_WORDS.add(word)

    extra_words = list()

    for word in STOP_WORDS:
        extra_words.append(word.title())
        extra_words.append(word.upper())

    for word in extra_words:
        STOP_WORDS.add(word)


def load_log():
    """Reads the processed comments log file and creates it if it doesn't exist.

    Returns
    -------
    list
        A list of Reddit comments ids.

   """

    try:
        with open(COMMENTS_LOG, "r", encoding="utf-8") as log_file:
            return log_file.read().splitlines()

    except FileNotFoundError:
        with open(COMMENTS_LOG, "a", encoding="utf-8") as log_file:
            return []


def update_log(comment_id):
    """Updates the processed comments log with the given comments id.

    Parameters
    ----------
    comment_id : str
        A Reddit post id.

    """

    with open(COMMENTS_LOG, "a", encoding="utf-8") as log_file:
        return log_file.write("{}\n".format(comment_id))


def init():
    """Inits the bot by fetching the inbox and replying with newly generated comments."""

    # Complete our stop words set.
    add_extra_words()

    # Load the model and remove prefixes that are commonly used by other bots.
    model = read_model(MODEL_FILE)
    model_keys = list(model.keys())

    for key in model_keys:
        if "^#" in key or "|" in key or "*****" in key or "^^" in key:
            del model[key]

    # We start the Reddit bot.
    reddit = praw.Reddit(client_id=config.APP_ID, client_secret=config.APP_SECRET,
                         user_agent=config.USER_AGENT, username=config.REDDIT_USERNAME,
                         password=config.REDDIT_PASSWORD)

    processed_comments = load_log()

    for comment in reddit.inbox.all(limit=100):

        if comment.author not in IGNORED_USERS and comment.id not in processed_comments:

            new_comment = generate_comment(model=model, order=2,
                                           number_of_sentences=2,
                                           initial_prefix=get_prefix_with_context(model, comment.body))

            # Small clean up when the bot uses Markdown and making sure the first letter is uppercase.
            new_comment = new_comment.replace(
                " > ", "\n\n > ").replace(" * ", "\n\n* ")

            new_comment = new_comment[0].upper() + new_comment[1:]

            if "[" not in new_comment and "]" in new_comment:
                new_comment = "[" + new_comment

            comment.reply(new_comment)
            update_log(comment.id)
            print("Replied to:", comment.id)


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


def get_prefix_with_context(model, context):
    """Get a random prefix that matches the given context.

    Parameters
    ----------
    model : dict
        The dictionary containing all the pairs and their possible outcomes.

    context : str
        A sentence which will be separated into keywords.

    Returns
    -------
    str
        The randomly selected context-aware prefix.

    """

    # Some light cleanup.
    context = context.replace("?", "").replace("!", "").replace(".", "")
    context_keywords = list(set(context.split()))

    # we remove stop words from the context.
    # We use reversed() to remove items from the list without affecting the sequence.
    for word in reversed(context_keywords):

        if len(word) <= 3 or word in STOP_WORDS:
            context_keywords.remove(word)

    # If our context has no keywords left we return a random prefix.
    if len(context_keywords) == 0:
        return get_prefix(model)

    # We are going to sample one prefix for each available keyword and return only one.
    model_keys = list(model.keys())
    random.shuffle(model_keys)
    sampled_prefixes = list()

    for word in context_keywords:

        for prefix in model_keys:

            if word in prefix or word.lower() in prefix or word.title() in prefix:
                
                if "?" not in prefix or "!" not in prefix or "." not in prefix:
                    sampled_prefixes.append(prefix)
                    break

    # If we don't get any samples we fallback to the random prefix method.
    if len(sampled_prefixes) == 0:
        return get_prefix(model)
    else:
        return random.choice(sampled_prefixes)


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
