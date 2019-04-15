"""
This script connects to the Pushshift API and downloads the complete comment history
of the given usernames and saves them to .csv files.
"""

import csv
import time
from datetime import datetime

import requests

# Try with your or your friends usernames (case insensitive).
USERNAMES = ["username_1", "username_2"]

HEADERS = {"User-Agent": "Comments Downloader v0.1"}
COMMENTS_LIST = list()


def init():
    """Initializes the csv.writer object and calls the load_comments function."""

    for username in USERNAMES:

        writer = csv.writer(open("./{}.csv".format(username),
                                 "w", newline="", encoding="utf-8"))

        # Adding the header.
        writer.writerow(["time", "date", "subreddit", "body"])

        print("Downloading:", username)
        load_comments(username=username)
        writer.writerows(COMMENTS_LIST)

        COMMENTS_LIST.clear()


def load_comments(username, latest_timestamp=None):
    """
    Downloads the username comments, 500 at a time.

    Parameters
    ----------
    username : str
        The Reddit username.

    latest_timestamp : int
        The latest comment timestamp.

    """

    # For the first url we don't provide the before parameter.
    if latest_timestamp == None:
        base_url = "https://api.pushshift.io/reddit/comment/search/?author={}&sort=desc&sort_type=created_utc&size=500".format(
            username)

    else:
        base_url = "https://api.pushshift.io/reddit/comment/search/?author={}&sort=desc&sort_type=created_utc&before={}&size=500".format(
            username, latest_timestamp)

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

            # We clean the greater-than and less-than and zero-width html code.
            body = item["body"].replace("&gt;", ">").replace(
                "&lt;", "<").replace("&amp;#x200B", " ")

            COMMENTS_LIST.append(
                [pub_time, pub_date, subreddit, body])

        if total_posts < 500:
            print("No more results.")
        else:
            time.sleep(1.2)
            load_comments(username, latest_timestamp)


if __name__ == "__main__":

    init()
