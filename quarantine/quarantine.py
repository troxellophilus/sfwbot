import argparse
import configparser
import glob
import json
import logging
import os

import praw


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nsfw-threshold", type=float, default=0.3, help="Minimum NSFW probability to cause a quarantine.")
    parser.add_argument("subreddit", help="Subreddit to download images from.")
    parser.add_argument("image_dir", help="Path to directory holding downloaded submission images.")
    return parser.parse_args()


_PRAW_BOT = "sfwbot"
_QUARANTINE_LIST = "quarantine.json"


def main():
    logging.basicConfig(level=logging.INFO)

    args = _parse_args()
    subreddit_id = args.subreddit
    proc_dir = args.image_dir
    nsfw_threshold = args.nsfw_threshold

    reddit = praw.Reddit(_PRAW_BOT)
    subreddit = reddit.subreddit(subreddit_id)

    with open(_QUARANTINE_LIST) as in_fo:
        already_quarantined = json.load(in_fo)
    quarantine = []

    result_glob = os.path.join(proc_dir, '*.result')
    val_idx = len('NSFW score:   ')
    for file_path in glob.glob(result_glob):
        with open(file_path) as in_fo:
            result = in_fo.read()  # type: str
        nsfw_prob = float(result[val_idx:])
        if nsfw_prob > nsfw_threshold:
            fullname = os.path.splitext(os.path.basename(file_path))[0]
            if not fullname in already_quarantined:
                quarantine.append(fullname)

    if quarantine:
        permalinks = []
        submissions = reddit.info(fullnames=quarantine)
        for submission in submissions:
            if hasattr(submission, 'approved_by'):
                logging.info(f"Submission '{submission.fullname}' approved by '{submission.approved_by}', skipping...")
                continue
            logging.info(f"Quarantining submission '{submission.fullname}' for being possibly nsfw.")
            submission.mod.nsfw()
            submission.mod.remove()
            permalinks.append(submission.permalink)
        if permalinks:
            logging.info(f"Sending alert message to subreddit moderators.")
            message = "The following submissions were quarantined for being possibly NSFW. If approved, a submission will be removed from the quarantine and will not be quarantined again.\n\n{}".format(
                '\n'.join(f'* {pl}' for pl in permalinks)
            )
            subreddit.message('SFWBot Quarantine Alert', message)
    else:
        logging.info("Did not find any NSFW submissions to quarantine.")


if __name__ == '__main__':
    main()
