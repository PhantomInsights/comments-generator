"""
This script connects to the Pushshift API and downloads the comment history
of the given subreddits and saves them to .csv files.
"""

import csv
import time
from datetime import datetime

import requests

# Try with your favorite subreddits (case insensitive).
SUBREDDITS = ["askreddit", "gaming"]

HEADERS = {"User-Agent": "Comments Downloader v0.1"}
COMMENTS_LIST = list()

# Set a maximum number of comments to download.
MAX_COMMENTS = 10000


def init():
    """Initializes the csv.writer object and calls the load_comments function."""

    for subreddit in SUBREDDITS:

        writer = csv.writer(open("./{}.csv".format(subreddit),
                                 "w", newline="", encoding="utf-8"))

        writer.writerow(["time", "date", "subreddit", "body"])

        print("Downloading:", subreddit)
        load_comments(subreddit=subreddit)
        writer.writerows(COMMENTS_LIST)

        COMMENTS_LIST.clear()


def load_comments(subreddit, latest_timestamp=None):
    """
    Downloads the subreddit comments, 500 at a time.

    Parameters
    ----------
    subreddit : str
        The subreddit name.

    latest_timestamp : int
        The latest comment timestamp.

    """

    # For the first url we don't provide the before parameter.
    if latest_timestamp == None:
        base_url = "https://api.pushshift.io/reddit/comment/search/?subreddit={}&sort=desc&sort_type=created_utc&size=500".format(
            subreddit)

    else:
        base_url = "https://api.pushshift.io/reddit/comment/search/?subreddit={}&sort=desc&sort_type=created_utc&before={}&size=500".format(
            subreddit, latest_timestamp)

    with requests.get(base_url, headers=HEADERS) as response:

        json_data = response.json()
        total_posts = len(json_data["data"])
        latest_timestamp = 0

        print("Downloading: {} comments".format(total_posts))

        for item in json_data["data"]:

            # We will only take 3 properties, the timestamp, subreddit and comment body.

            latest_timestamp = item["created_utc"]

            pub_time = datetime.fromtimestamp(
                latest_timestamp).strftime("%H:%M:%S")

            pub_date = datetime.fromtimestamp(
                latest_timestamp).strftime("%Y-%m-%d")

            subreddit = item["subreddit"]

            # We clean the greater-than and less-than html code.
            body = item["body"].replace("&gt;", ">").replace("&lt;", "<")

            COMMENTS_LIST.append(
                [pub_time, pub_date, subreddit, body])

        if total_posts < 500:
            print("No more results.")
        elif len(COMMENTS_LIST) >= MAX_COMMENTS:
            print("Download complete.")
        else:
            time.sleep(1.2)
            load_comments(subreddit, latest_timestamp)


if __name__ == "__main__":

    init()
