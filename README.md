# Comments Generator

This project consists of a Reddit bot that replies to users with newly generated context-aware comments using `Markov chains` trained from existing comments of subreddits and users you desire. 

The main purpose of this project was to document the extraction, transformation and load process (`ETL`) of Reddit comments and to create the foundation for a very simple chat bot.

The project is divided in 3 main parts, the `ETL` process, the generation of the training model and its use to generate new comments and post them on Reddit.

The most important files are:

* `step1.py` : A Python script that downloads the complete comment history from the given Reddit usernames using the Pushshift API.

* `step1_alt.py` : A Python script that downloads an specified amount of comments from the given subreddits using the Pushshift API.

* `step2.py` : A Python script that reads the generated .csv files from step1.py/step1_alt.py, applies some light clean up and computes their contents into a training model.

* `step2_alt.py` : A Python script that reads specified .txt files and computes their contents into a training model. This script is recommended if your text sources are not Reddit comments. 

* `bot.py` : A Reddit bot that checks its inbox for new replies, mentions and private messages and replies to them with newly generated comments using the training model.

* `step3.py` : A Python script that generates new sentences using the training model. This script is recommended if you only want to see the results and don't need a Reddit bot.

This project uses the following Python libraries

* `PRAW` : Makes the use of the Reddit API very easy.
* `Requests` : Used to download comments from the Pushshift API.

## ETL Process

The `Pushshift` API allows us to download `Reddit` comments in batches of 500, this is really useful when we plan to download tens of thousands of comments.

This project includes 2 methods to get comments, either users comments or subreddits comments.

### Users Comments

For these kind of small scripts I like to use a *global* list that I can manipulate anywhere in the program. On bigger projects this can be an issue if not correctly structured.

We start by iterating over the desired usernames and creating a `csv.writer` object.

```python
for username in USERNAMES:

    writer = csv.writer(open("./{}.csv".format(username),
                                 "w", newline="", encoding="utf-8"))

    # Adding the header.
    writer.writerow(["time", "date", "subreddit", "body"])

    load_comments(username=username)
```

The script downloads 500 comments at a time in reverse chronological order until it doesn't have any more comments to download.

From each comment I extract 3 fields, timestamp, subreddit and the comment body.

*Note: Currently the date and time are not used in this project, I added them to verify that I was getting the comments in the order I desired but they can be useful for future projects.*

Those 3 fields are then packed into a list and added to the *global* list.

```python
for item in json_data["data"]:

    latest_timestamp = item["created_utc"]

    pub_time = datetime.fromtimestamp(
        latest_timestamp).strftime("%H:%M:%S")

    pub_date = datetime.fromtimestamp(
        latest_timestamp).strftime("%Y-%m-%d")

    subreddit = item["subreddit"]
    body = item["body"]

    COMMENTS_LIST.append([pub_time, pub_date, subreddit, body])
```

Once the script finishes downloading all the comments from the current user it calls the `csv.writer.writerows()` method with the contents of the *global* list, clears the *global* list and moves to the next user.

### Subreddits Comments

This script is very similar to the previous one, the main diffecence is that we don't specify which users comments we want to download, instead we download comments from all the users that participated in the given subreddits.

The default maximum amount of comments has been set to 20,000. I found this number to be good enough for creating the training model.

The script will attempt to download the defined maximum amount of comments and in case the subreddit has fewer comments the script will save them as usual and move to the next subreddit.

## Understanding Markov Chains

Before moving to more code I need to explain a few very important things about Markov chains.

Markov chains can have a *variable length memory*, this is very useful to generate real looking texts.

The proper name of this memory is *order*, the greater is the number of the order the more realistic the generated text will be but it will have the side effect of having less outcomes.

To better illustrate the difference we are going to use the following paragraph from Lou Gehrig farewell to baseball speech to create a first and second-order Markov chains and models.

> Fans, for the past two weeks you have been reading about a bad break I got. Yet today I consider myself the luckiest man on the face of the earth. I have been in ballparks for seventeen years and have never received anything but kindness and encouragement from you fans.

### First-order

```python
{
    'Fans,': ['for'],
    'for': ['the', 'seventeen'],
    'the': ['past','luckiest', 'face', 'earth.'],
    'past': ['two'],
    'two': ['weeks'],
    'weeks': ['you'],
    'you': ['have', 'fans.'],
    'have': ['been', 'been', 'never'],
    'been': ['reading', 'in'],
    'reading': ['about'],
    'about': ['a'],
    'a': ['bad'],
    'bad': ['break'],
    'break': ['I'],
    'I': ['got.', 'consider', 'have'],
    'got.': ['Yet'],
    'Yet': ['today'],
    'today': ['I'],
    'consider': ['myself'],
    'myself': ['the'],
    'luckiest': ['man'],
    'man': ['on'],
    'on': ['the'],
    'face': ['of'],
    'of': ['the'],
    'earth.': ['I'],
    'in': ['ballparks'],
    'ballparks': ['for'],
    'seventeen': ['years'],
    'years': ['and'],
    'and': ['have', 'encouragement'],
    'never': ['received'],
    'received': ['anything'],
    'anything': ['but'],
    'but': ['kindness'],
    'kindness': ['and'],
    'encouragement': ['from'],
    'from': ['you']
}
```

With first-order Markov chains we can have multiple outcomes for each state (word) and we can generate sentences like these ones:

* Yet today I have been in ballparks for the earth. I consider myself the past two weeks you fans.

* Fans, for seventeen years and have been reading about a bad break I have never received anything but kindness and have been in ballparks for the earth.

* Yet today I have been in ballparks for seventeen years and encouragement from you fans. Yet today I have been reading about a bad break I got.

The previous sentences sometimes can make a little bit of sense but if our goal is to generate realistic looking ones we can use a second-order chain.

### Second-order

```python
{
    'Fans, for': ['the'],
    'for the': ['past'],
    'the past': ['two'],
    'past two': ['weeks'],
    'two weeks': ['you'],
    'weeks you': ['have'],
    'you have': ['been'],
    'have been': ['reading', 'in'],
    'been reading': ['about'],
    'reading about': ['a'],
    'about a': ['bad'],
    'a bad': ['break'],
    'bad break': ['I'],
    'break I': ['got.'],
    'I got.': ['Yet'],
    'got. Yet': ['today'],
    'Yet today': ['I'],
    'today I': ['consider'],
    'I consider': ['myself'],
    'consider myself': ['the'],
    'myself the': ['luckiest'],
    'the luckiest': ['man'],
    'luckiest man': ['on'],
    'man on': ['the'],
    'on the': ['face'],
    'the face': ['of'],
    'face of': ['the'],
    'of the': ['earth.'],
    'the earth.': ['I'],
    'earth. I': ['have'],
    'I have': ['been'],
    'been in': ['ballparks'],
    'in ballparks': ['for'],
    'ballparks for': ['seventeen'],
    'for seventeen': ['years'],
    'seventeen years': ['and'],
    'years and': ['have'],
    'and have': ['never'],
    'have never': ['received'],
    'never received': ['anything'],
    'received anything': ['but'],
    'anything but': ['kindness'],
    'but kindness': ['and'],
    'kindness and': ['encouragement'],
    'and encouragement': ['from'],
    'encouragement from': ['you'],
    'from you': ['fans.']
}
```

We can observe that we only have one instance where the outcome can be 50/50: `'have been': ['reading', 'in']`.

* Yet today I consider myself the luckiest man on the face of the earth. I have been in ballparks for seventeen years and have never received anything but kindness and encouragement from you fans.

* I consider myself the luckiest man on the face of the earth. I have been reading about a bad break I got.

The results look more natural but we will soon realize the chain is identical to the original text.

This is why it is very important to collect a high amount of data.

## Generating the Model

Now that we have seen the difference between first and second order Markov chains we can continue with the model generation.

The step2.py/step2_alt.py scripts allows us to define the order. The default one is 2 (second-order).

We will also have to define which .csv files we want to process. I have implemented a filter mechanism where we can define which subreddits we want to allow, this is to filter out subreddits with NSFW or undesired content.

We then start iterating over all .csv files using the `csv.DictReader` class.

Some light clean up is made to ensure all comments don't have whitespaces around them and making sure all comments end with punctuation.

```python
word_dictionary = dict()
comments_list = list()

for csv_file in CSV_FILES:

    # We iterate the .csv row by row.
    for row in csv.DictReader(open(csv_file, "r", encoding="utf-8")):

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
```

After we have cleaned up the comment we add it to a master list.

This list is then merged into one big string that will then be split into individual words.

The purpose of this is to increase the number of outcomes.

```python
comments_list.append(row["body"])

# We separate each comment into words.
words_list = " ".join(comments_list).split()
```

Creating the model is actually not hard. We only require to have a way to know the current index of each word in the `word_list`. The `enumerate` built-in function will be perfect for this task.

We first define our prefix, which is the current word plus the next word(s) equal to the order number.

Since Python slicing is exclusive on the end part, we don't have to do anything extra. 

Then we define our suffix, which is very similar to calculate as the prefix.

```python
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
```

If our prefix is not in the `word_dictionary` we initiate it with a list containing the current suffix.

Alternatively, if the prefix is already in the dictionary we just append the current suffix to its inner list.

Finally we save the dictionary using the `pickle` module. This will save us time when reusing it on other Python scripts.

*Note: If you want to create training models from other text sources such as tweets, books or chat logs you can use step2_alt.py instead. The script takes the contents of the specified .txt files, merges them and compiles the model in the same way as in step2.py*

## Reddit Bot

This bot is simple in nature, it checks its inbox every minute for new unread messages and replies to them.

We first define a list of users to ignore, this is very important to avoid engaging in infinite conversations with another bots and to avoid errors.

Then we create a `STOP_WORDS` set and add all our desired stop words in uppercase, lowercase and title form. Those will be used later to aid in the context-aware part.

After that we load the `pickle` file into memory and remove some prefixes that are known to be used by other bots.

```python
# Complete our stop words set.
add_extra_words()

# Load the model and remove prefixes that are commonly used by other bots.
model = read_model(MODEL_FILE)
model_keys = list(model.keys())

for key in model_keys:
    if "^#" in key or "|" in key or "*****" in key:
        del model[key]
```

With our model ready we start a `Reddit` object using the `PRAW` library and check our inbox and reply to new messages.


```python
reddit = praw.Reddit(client_id=config.APP_ID, client_secret=config.APP_SECRET,
                     user_agent=config.USER_AGENT, username=config.REDDIT_USERNAME,
                     password=config.REDDIT_PASSWORD)

processed_comments = load_log()

for comment in reddit.inbox.all(limit=100):

    if comment.author not in IGNORED_USERS and comment.id not in processed_comments:

        new_comment = generate_comment(model=model, order=2,
                                       number_of_sentences=2,
                                       initial_prefix=get_prefix_with_context(model, comment.body))

        # Small clean up when the bot uses Markdown.
        new_comment = new_comment.replace(
            " > ", "\n\n > ").replace(" * ", "\n\n* ")

        comment.reply(new_comment)
        update_log(comment.id)
        print("Replied to:", comment.id)
```

The most important functions to generate the new comment are `get_prefix_with_context()` and `generate_comment()`.

The `get_prefix_with_context()` function tries to get a prefix that matches the given context which can be a previous comment or an arbitrary string.

To achieve this we first clean the context by removing stop words and punctuation marks.

Once cleaned we shuffle the model prefixes and sample one prefix for each remaining word in the context.

Finally we choose one of the sampled prefixes and return it. 

```python
def get_prefix_with_context(model, context):

    # Some light cleanup.
    context = context.replace("?", "").replace("!", "").replace(".", "")
    context_keywords = context.split()

    # we remove stopwords from the context.
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
                sampled_prefixes.append(prefix)
                break

    # If we don't get any samples we fallback to the random prefix method.
    if len(sampled_prefixes) == 0:
        return get_prefix(model)
    else:
        return random.choice(sampled_prefixes)
```

When the previous function fails to get a prefix it fallbacks to `get_prefix()`, this function tries to get a prefix that meets 2 conditions.

1. The prefix must start with an uppercase letter.
2. The prefix must not end with a punctuation mark.

```python
def get_prefix(model):

    model_keys = list(model.keys())

    # We give it a maximum of 10,000 tries.
    for i in range(10000):

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
```

This function is mostly a personal preference. I found out that if the starting prefix matches both conditions the rest of the chain will look more natural.

You are free to specify other prefix as the `initial_prefix`. In step3.py I included an example of each 3 possible methods.

And finally, we have the function that constructs the chain.

We first start the chain with the `initial_prefix` and choose one random suffix from it.

Then we extract the latest suffix from the ongoing chain and request the next suffix, we repeat until we hit a suffix that has a punctuation mark.

Once we got the desired number of sentences we break the loop and return our newly generated string of text.

I added a small fail-safe of 500 max suffixes in case we go infinite.

```python
def generate_comment(model, number_of_sentences, initial_prefix, order):

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
```

To extract the latest suffix from the chain we will use the handy reverse slicing method `[-order:]`.

*Note: If you don't want to use a Reddit bot and only want to see the results I recommend using step3.py, this script does exactly the same as bot.py but removes all Reddit specific code.*

## Conclusion

I hope you have enjoyed the article, this project was something I wanted to do for a long time and I'm glad it worked better than what I expected.

If you plan to deploy the bot on Reddit, I strongly suggest that you read the [Bottiquette](https://www.reddit.com/r/Bottiquette/wiki/bottiquette). You are welcome to use [my subreddit](https://www.reddit.com/r/PhantomAppDev) to test your bot.

[![Become a Patron!](https://c5.patreon.com/external/logo/become_a_patron_button.png)](https://www.patreon.com/bePatron?u=20521425)