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

from .rss_utils import get_entries

BASE_DIR_PATH = Path(__file__).parent.parent
ARCHIVE_DIR_PATH = BASE_DIR_PATH / "archive"

load_dotenv(BASE_DIR_PATH / ".env")


def post(content: str, discord_webhook_url: str, discord_channel_id: str) -> None:
    requests.post(
        discord_webhook_url, json={"content": content, "channel_id": discord_channel_id}
    )


def main() -> None:
    ARCHIVE_DIR_PATH.mkdir(exist_ok=True)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--task-file", type=str, default="task.json", help="URL list")
    parser.add_argument(
        "--discord-webhook",
        action="store_true",
        help="Post messages to Discord servers",
    )
    parser.add_argument("--clear", action="store_true", help="Clear archive directory")
    parser.add_argument(
        "--line-length-limit", type=int, default=100, help="Line length limit of diff"
    )
    parser.add_argument("--task-name", type=str, help="Select a task")
    parser.add_argument(
        "--no-archive", action="store_true", help="Do not archive sites"
    )
    parser.add_argument("--show", action="store_true", help="Show content")
    args = parser.parse_args()

    deepl_api_key = os.getenv("DEEPL_API_KEY")
    translator = deepl.Translator(deepl_api_key) if deepl_api_key is not None else None

    default_discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    TASK_FILE_PATH = BASE_DIR_PATH / args.task_file
    tasks = json.load(TASK_FILE_PATH.open())

    if args.clear:
        for f in ARCHIVE_DIR_PATH.glob("*"):
            f.unlink()

    for task in tasks:
        task_name = task.get("task_name", False)
        if args.task_name and args.task_name != task_name:
            continue
        disable = task.get("disable", False)
        if disable:
            continue

        url = task.get("url", None)
        if url is not None:
            url = url.strip()
        command = task.get("command", None)
        script = task.get("script", None)
        page_type = task.get("type", None)
        page_title = task.get("title", None)
        pattern = task.get("pattern", None)
        translate = task.get("translate", False)
        count = task.get("count", False)
        discord_channel_id = task.get("discord_channel_id", None)
        number_of_context_lines = task.get("number_of_context_lines", 1)
        quoted = task.get("quoted", True)
        discord_webhook_url = task.get(
            "discord_webhook_url", default_discord_webhook_url
        )

        if task_name is None:
            task_name = url
        if task_name is None:
            task_name = str(command)
        if task_name is None:
            task_name = str(script)

        print(f"[+] {task_name}")

        filename = hashlib.md5(task_name.encode()).hexdigest()[:8]
        filepath = ARCHIVE_DIR_PATH / filename

        match page_type:
            case "rss":
                feed_title, entries = get_entries(url)
                if page_title is None:
                    page_title = feed_title

                if len(entries) == 0:
                    continue

                if count:
                    entries = entries[:count]

                if filepath.exists():
                    known_titles = [
                        line.strip() for line in filepath.open().readlines()
                    ]
                else:
                    known_titles = []

                for title, url, description in entries[::-1]:
                    if title in known_titles:
                        continue

                    if translate and translator is not None:
                        description = str(
                            translator.translate_text(description, target_lang="JA")
                        )

                    if args.discord_webhook:
                        if quoted:
                            post(
                                f"[{page_title}] {title} {url}\n```{description}```",
                                discord_webhook_url,
                                discord_channel_id,
                            )
                        else:
                            post(
                                f"[{page_title}] {title} {url}\n{description}",
                                discord_webhook_url,
                                discord_channel_id,
                            )
                    else:
                        print(f"[{page_title}] {title} {url}\n{description}")
                        print()

                    if not args.no_archive:
                        filepath.open("a").write(title + "\n")
            case _:
                if page_type == "command":
                    response = subprocess.run(
                        command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
                    )
                    if response.returncode != 0:
                        continue
                    raw_content = response.stdout
                elif page_type == "python script":
                    response = subprocess.run(
                        [sys.executable, BASE_DIR_PATH / script],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                    )
                    if response.returncode != 0:
                        continue
                    raw_content = response.stdout
                elif page_type == "text":
                    response = requests.get(url)

                    if response.status_code != 200:
                        continue

                    raw_content = response.content
                
                else:
                    print(f"Unknown page type: {page_type}")
                    continue

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

                    diff = list(
                        difflib.unified_diff(
                            prev_content,
                            content,
                            "",
                            "",
                            n=number_of_context_lines,
                            lineterm="",
                        )
                    )[2:]
                    diff_res = ""
                    for line in diff:
                        n = args.line_length_limit
                        if len(line) > n:
                            diff_res += (
                                line[: n // 2] + " ... " + line[-n // 2 :] + "\n"
                            )
                        else:
                            diff_res += line + "\n"

                    if diff_res != "":
                        if args.discord_webhook:
                            if quoted:
                                post(
                                    f"UPDATED: {task_name}\n```{diff_res}```",
                                    discord_webhook_url,
                                    discord_channel_id,
                                )
                            else:
                                post(
                                    f"UPDATED: {task_name}\n{diff_res}",
                                    discord_webhook_url,
                                    discord_channel_id,
                                )
                        else:
                            print(f"UPDATED: {task_name}\n{diff_res}")
                            print()
                else:
                    if args.discord_webhook:
                        post(
                            f"NEW: {task_name}", discord_webhook_url, discord_channel_id
                        )
                    else:
                        print(f"NEW: {task_name}")
                        print()

                if not args.no_archive:
                    filepath.open("wb").write(raw_content)


if __name__ == "__main__":
    main()
