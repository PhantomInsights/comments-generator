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
        writer.writerow(["datetime", "subreddit", "body"])

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

    base_url = "https://api.pushshift.io/reddit/comment/search/"
    
    params = {"author": username, "sort": "desc",
              "sort_type": "created_utc", "size": 500}

    # After the first call of this function we will use the 'before' parameter.
    if latest_timestamp != None:
        params["before"] = latest_timestamp

    with requests.get(base_url, params=params, headers=HEADERS) as response:

        json_data = response.json()
        total_posts = len(json_data["data"])
        latest_timestamp = 0

        print("Downloading: {} comments".format(total_posts))

        for item in json_data["data"]:

            # We will only take 3 properties, the timestamp, subreddit and comment body.

            latest_timestamp = item["created_utc"]

            iso_date = datetime.fromtimestamp(latest_timestamp)

            subreddit = item["subreddit"]

            # We clean the greater-than and less-than and zero-width html code.
            body = item["body"].replace("&gt;", ">").replace(
                "&lt;", "<").replace("&amp;#x200B", " ")

            COMMENTS_LIST.append(
                [iso_date, subreddit, body])

        if total_posts < 500:
            print("No more results.")
        else:
            time.sleep(1.2)
            load_comments(username, latest_timestamp)


if __name__ == "__main__":

    init()
