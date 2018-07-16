# TODO: Extract all images from url rather than just downloading the url.

import argparse
import configparser
import imghdr
import logging
import mimetypes
import os
import sys

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
    config_file = _cwd_join('nsfwdetectbot.ini')
    conf.read(config_file)
    load_config.conf = conf

    return load_config.conf


_PRAW_BOT = "nsfwdetectbot"


def main():
    logging.basicConfig(level=logging.INFO)

    conf = load_config()
    target_subreddit = conf['nsfwdetectbot']['subreddit']
    submission_limit = int(conf['nsfwdetectbot']['submission_limit'])
    work_dir = conf['nsfwdetectbot']['work_dir']

    reddit = praw.Reddit(_PRAW_BOT)

    submissions = reddit.subreddit(target_subreddit).new(limit=submission_limit)

    for submission in submissions:
        try:
            out_file = os.path.join(work_dir, submission.fullname)
            download_image(submission.url, out_file)
            logging.info("Downloaded image from submission '{}'.".format(submission.fullname))
        except ValueError as err:
            logging.info("Skipped submission '{}': {}".format(submission.fullname, err))


if __name__ == '__main__':
    main()
