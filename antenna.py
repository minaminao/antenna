import argparse
import difflib
import hashlib
import re
from pathlib import Path

import feedparser
import requests

from rss_utils import *

BASE_DIR_PATH = Path(__file__).parent
ARCHIVE_DIR_PATH = BASE_DIR_PATH / "archive"


def main():
    ARCHIVE_DIR_PATH.mkdir(exist_ok=True)

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--url_file", type=str, default="url.txt", help="URL list")
    parser.add_argument("--discord_webhook_url", type=str, help="Discord webhook URL")
    parser.add_argument("--sample", action="store_true", help="Use sample URL list")
    parser.add_argument("--clear", action="store_true", help="Clear archive directory")
    parser.add_argument("--line_length_limit", type=int, default=100, help="Line length limit of diff")
    parser.add_argument("--number_of_context_lines", type=int, default=1, help="Number of context lines")
    parser.add_argument("--no_archive", action="store_true", help="Do not archive sites")
    parser.add_argument("--show", action="store_true", help="Show content")
    args = parser.parse_args()


    if args.sample:
        SITEURL_SAMPLE_PATH = BASE_DIR_PATH / "url_sample.txt"
        tasks = [line.strip().split(",", 1) for line in SITEURL_SAMPLE_PATH.open().readlines() if line.strip() != ""]
    else:
        SITEURL_PATH = BASE_DIR_PATH / args.url_file
        tasks = [line.strip().split(",", 1) for line in SITEURL_PATH.open().readlines() if line.strip() != ""]

    if args.clear:
        for f in ARCHIVE_DIR_PATH.glob("*"):
            f.unlink()

    for task in tasks:
        url = task[0].strip()
        pattern = task[1].strip() if len(task) > 1 else None
        filename = hashlib.md5(url.encode()).hexdigest()[:8]
        filepath = ARCHIVE_DIR_PATH / filename

        if pattern == "rss":
            entries = get_entries(url)

            if len(entries) == 0:
                continue

            if filepath.exists():
                known_titles = [line.strip() for line in filepath.open().readlines()]
            else:
                known_titles = []
                
            for title, url, description in entries[::-1]:
                if title in known_titles[-len(entries):]:
                    continue

                if args.discord_webhook_url:
                    requests.post(args.discord_webhook_url, json={"content": f"{title}\n{url}\n```{description}```"})
                else:
                    print(title)
                    print(url)
                    print(description)
                    print()

                if not args.no_archive:
                    filepath.open("a").write(title + "\n")

        else:
            response = requests.get(url)

            if response.status_code != 200:
                continue

            if not pattern:
                content = response.content.decode().split("\n")
            else:
                content = re.findall(pattern, response.content.decode())

            if args.show:
                print(f"content = {content}")

            if filepath.exists():
                if not pattern:
                    prev_content = filepath.open("r").read().split("\n")
                else:
                    prev_content = re.findall(pattern, filepath.open("r").read())

                diff = difflib.unified_diff(prev_content, content, "Previous", "Current", n=args.number_of_context_lines, lineterm="")
                diff_res = ""
                for line in diff:
                    n = args.line_length_limit
                    if len(line) > n:
                        diff_res += line[:n//2] + " ... " + line[-n//2:] + "\n"
                    else:
                        diff_res += line + "\n"

                if diff_res != "":
                    if args.discord_webhook_url:
                        requests.post(args.discord_webhook_url, json={"content": f"UPDATED: {url}\n```{diff_res}```"})
                    else:
                        print(f"UPDATED: {url}")
                        print(diff_res)
                        print()

            if not args.no_archive:
                filepath.open("wb").write(response.content)


if __name__ == "__main__":
    main()
