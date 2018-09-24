# TODO: Extract all images from url rather than just downloading the url.

import argparse
import configparser
import imghdr
import logging
import mimetypes
import os
import shutil
import sys
import tempfile
from typing import BinaryIO

import praw
import requests


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


def _root_join(*args):
    _root = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(_root, *args)


def _cwd_join(*args):
    _cwd = os.path.abspath(os.getcwd())
    return os.path.join(_cwd, *args)


def load_config():
    if hasattr(load_config, 'conf'):
        return load_config.conf
    conf = configparser.ConfigParser()
    config_file = _cwd_join('sfwbot.ini')
    conf.read(config_file)
    load_config.conf = conf

    return load_config.conf


_PRAW_BOT = "sfwbot"


def main():
    logging.basicConfig(level=logging.INFO)

    conf = load_config()
    target_subreddit = conf['sfwbot']['subreddit']
    submission_limit = int(conf['sfwbot']['submission_limit'])
    out_loc = conf['sfwbot']['temp_location']

    reddit = praw.Reddit(_PRAW_BOT)

    submissions = reddit.subreddit(target_subreddit).new(limit=submission_limit)

    with tempfile.TemporaryDirectory() as tmp_dir:
        for submission in submissions:
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
