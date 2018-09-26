# TODO: Extract all images from url rather than just downloading the url.

import argparse
import configparser
import imghdr
import json
import logging
import mimetypes
import os
import shutil
import sys
import tempfile
from typing import BinaryIO

import praw
import requests


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission-limit", type=int, default=10, help="Maximum number of new submissions to check in a batch.")
    parser.add_argument("subreddit", help="Subreddit to download images from.")
    parser.add_argument("image_dir", help="Path to a directory to hold image files.")
    return parser.parse_args()


def download_image(url, filename):
    """Download an image from a URL to a filename.

    Handles imgur special case (forces extension).

    Raises errors if the mimetype or headers aren't an image.

    Args:
        url (str): URL of the image to download.
        filename (str): Output file name.

    Raises:
        ValueError: If the mime type of the URL or the header of the file are not images.
    """
    if not url:
        raise ValueError("url required.")
    if 'imgur' in url:
        url = "{}.jpg".format(url)
    mime_type, _ = mimetypes.guess_type(url)
    if not (mime_type and 'image' in mime_type):
        raise ValueError("Mime type of url '{}' is not an image.".format(url))
    response = requests.get(url)
    with open(filename, 'wb') as fo:
        for chunk in response.iter_content():
            fo.write(chunk)
    if not imghdr.what(filename):
        os.remove(filename)
        raise ValueError("Header of file '{}' is not an image.".format(filename))


def store_file(file_obj: BinaryIO, out_path: str):
    with open(out_path, 'wb') as out_fo:
        shutil.copyfileobj(file_obj, out_fo)


def read_config(file_path):
    conf = configparser.ConfigParser()
    conf.read(file_path)
    return conf


_PRAW_BOT = "sfwbot"
_QUARANTINE_LIST = "quarantine.json"
_SAFE_LIST = "safe.json"


def main():
    logging.basicConfig(level=logging.INFO)

    args = _parse_args()
    target_subreddit = args.subreddit
    submission_limit = args.submission_limit
    out_loc = args.image_dir

    with open(_QUARANTINE_LIST) as in_fo:
        quarantine = json.load(in_fo)
    with open(_SAFE_LIST) as in_fo:
        safe = json.load(in_fo)

    reddit = praw.Reddit(_PRAW_BOT)

    submissions = reddit.subreddit(target_subreddit).new(limit=submission_limit)

    with tempfile.TemporaryDirectory() as tmp_dir:
        for submission in submissions:
            if submission.fullname in quarantine or submission.fullname in safe:
                logging.info("Already processed {}, skipping.".format(submission.fullname))
                continue
            try:
                out_file = os.path.join(tmp_dir, submission.fullname)
                download_image(submission.url, out_file)
                logging.info("Downloaded image from submission '{}'.".format(submission.fullname))
            except ValueError as err:
                logging.info("Skipped submission '{}': {}".format(submission.fullname, err))
        for file_name in os.listdir(tmp_dir):
            file_path = os.path.join(tmp_dir, file_name)
            with open(file_path, 'rb') as in_fo:
                out_path = os.path.join(out_loc, os.path.basename(file_path))
                store_file(in_fo, out_path)


if __name__ == '__main__':
    main()
