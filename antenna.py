from pathlib import Path
import argparse
import requests
import hashlib
import difflib

BASE_DIR_PATH = Path(__file__).parent
ARCHIVE_DIR_PATH = BASE_DIR_PATH / "archive"


def main():
    ARCHIVE_DIR_PATH.mkdir(exist_ok=True)

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--url_file", type=str, default="url.txt", help="URL list")
    parser.add_argument("--discord_webhook_url", type=str, help="Discord webhook URL")
    parser.add_argument("--sample", action="store_true", help="Use sample URL list")
    parser.add_argument("--clear", action="store_true", help="Clear archive directory")
    args = parser.parse_args()


    if args.sample:
        SITEURL_SAMPLE_PATH = BASE_DIR_PATH / "url_sample.txt"
        urls = [line.strip() for line in SITEURL_SAMPLE_PATH.open().readlines() if line.strip() != ""]
    else:
        SITEURL_PATH = BASE_DIR_PATH / args.url_file
        urls = [line.strip() for line in SITEURL_PATH.open().readlines() if line.strip() != ""]

    if args.clear:
        for f in ARCHIVE_DIR_PATH.glob("*"):
            f.unlink()

    for url in urls:
        response = requests.get(url)

        if response.status_code != 200:
            continue

        content = response.content.decode().split("\n")
        filename = hashlib.md5(url.encode()).hexdigest()[:8]
        filepath = ARCHIVE_DIR_PATH / filename

        if filepath.exists():
            prev_content = filepath.open("r").read().split("\n")

            diff = difflib.unified_diff(prev_content, content, "old", "new", lineterm="")
            diff_res = "\n".join(diff)

            if diff_res != "":
                if args.discord_webhook_url:
                    requests.post(args.discord_webhook_url, json={"content": f"UPDATED: {url}\n```{diff_res}```"})
                else:
                    print(f"UPDATED: {url}")
                    print(diff_res)
                    print()

        filepath.open("wb").write(response.content)


if __name__ == "__main__":
    main()
