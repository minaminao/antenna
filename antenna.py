import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import deepl
import requests
from dotenv import load_dotenv

from rss_utils import *

load_dotenv()

BASE_DIR_PATH = Path(__file__).parent
ARCHIVE_DIR_PATH = BASE_DIR_PATH / "archive"


def main():
    ARCHIVE_DIR_PATH.mkdir(exist_ok=True)

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--url_file", type=str, default="url.json", help="URL list")
    parser.add_argument("--discord_webhook", action="store_true", help="Notify Discord using local webhook url file")
    parser.add_argument("--discord_webhook_url", type=str, help="Discord webhook URL")
    # parser.add_argument("--discord_bot", action="store_true", help="Notify Discord using discord bot")
    # parser.add_argument("--discord_bot_api_key", type=str, help="Discord bot API key")
    parser.add_argument("--sample", action="store_true", help="Use sample URL list")
    parser.add_argument("--clear", action="store_true", help="Clear archive directory")
    parser.add_argument("--line_length_limit", type=int, default=100, help="Line length limit of diff")
    parser.add_argument("--number_of_context_lines", type=int, default=1, help="Number of context lines")
    parser.add_argument("--task_name", type=str, help="Select a task name")
    parser.add_argument("--no_archive", action="store_true", help="Do not archive sites")
    parser.add_argument("--show", action="store_true", help="Show content")
    args = parser.parse_args()

    deepl_api_key = os.getenv("DEEPL_API_KEY")
    translator = deepl.Translator(deepl_api_key) if deepl_api_key else None
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if args.discord_webhook_url:
        discord_webhook_url = args.discord_webhook_url
    # discord_bot_api_key = os.getenv("DISCORD_BOT_API_KEY")
    # if args.discord_bot_api_key:
    #     discord_bot_api_key = args.discord_bot_api_key

    if args.sample:
        SITEURL_SAMPLE_PATH = BASE_DIR_PATH / "url_sample.json"
        tasks = json.load(SITEURL_SAMPLE_PATH.open())
    else:
        SITEURL_PATH = BASE_DIR_PATH / args.url_file
        tasks = json.load(SITEURL_PATH.open())

    if args.clear:
        for f in ARCHIVE_DIR_PATH.glob("*"):
            f.unlink()

    for task in tasks:
        url = task.get("url", None)
        if url is not None: 
            url = url.strip()
        disable = task.get("disable", False)
        if disable:
            continue
        task_name = task.get("task_name", False)
        if args.task_name and args.task_name != task_name:
            continue
        command = task.get("command", None)
        script = task.get("script", None)
        page_type = task.get("type", None)
        page_title = task.get("title", None)
        pattern = task.get("pattern", None)
        translate = task.get("translate", False)
        count = task.get("count", False)
        discord_channel_id = task.get("discord_channel_id", None)

        if task_name is None:
            task_name = url
        if task_name is None:
            task_name = str(command)
        if task_name is None:
            task_name = str(script)

        filename = hashlib.md5(task_name.encode()).hexdigest()[:8]
        filepath = ARCHIVE_DIR_PATH / filename

        if page_type == "rss":
            feed_title, entries = get_entries(url)
            if page_title is None:
                page_title = feed_title

            if len(entries) == 0:
                continue

            if count:
                entries = entries[:count]

            if filepath.exists():
                known_titles = [line.strip() for line in filepath.open().readlines()]
            else:
                known_titles = []

            for title, url, description in entries[::-1]:
                if title in known_titles:
                    continue

                if translate and translator is not None:
                    description = str(translator.translate_text(description, target_lang="JA"))

                if args.discord_webhook:
                    requests.post(discord_webhook_url, json={
                        "content": f"[{page_title}] {title} {url}\n```{description}```",
                        "channel_id": discord_channel_id
                    })
                else:
                    print(f"[{page_title}] {title} {url}\n{description}")
                    print()

                if not args.no_archive:
                    filepath.open("a").write(title + "\n")
        else:
            if page_type == "command":
                response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                raw_content = response.stdout
            elif page_type == "python script":
                print([sys.executable, script]
                )
                response = subprocess.run([sys.executable, script], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                raw_content = response.stdout
            else:
                response = requests.get(url)

                if response.status_code != 200:
                    continue

                raw_content = response.content

            if not pattern:
                content = raw_content.decode().split("\n")
            else:
                content = re.findall(pattern, raw_content.decode())

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
                        diff_res += line[:n // 2] + " ... " + line[-n // 2:] + "\n"
                    else:
                        diff_res += line + "\n"

                if diff_res != "":
                    if args.discord_webhook:
                        requests.post(discord_webhook_url, json={
                            "content": f"UPDATED: {task_name}\n```{diff_res}```",
                            "channel_id": discord_channel_id
                        })
                    else:
                        print(f"UPDATED: {task_name}\n{diff_res}")
                        print()
            else:
                if args.discord_webhook:
                    requests.post(discord_webhook_url, json={
                        "content": f"NEW: {task_name}",
                        "channel_id": discord_channel_id
                    })
                else:
                    print(f"NEW: {task_name}")
                    print()

            if not args.no_archive:
                filepath.open("wb").write(raw_content)


if __name__ == "__main__":
    main()
