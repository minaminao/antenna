# antenna
サイトを巡回して更新があったらDiscordに教えてくれる君。

## Usage

```
$ crontab -e
```

```
* * * * * <Pythonの絶対パス> <antenna.pyの絶対パス> --discord_webhook_url <Discord webhook URL>
```

### Options

```
usage: antenna.py [-h] [--url_file URL_FILE] [--discord_webhook_url DISCORD_WEBHOOK_URL] [--sample] [--clear]

options:
  -h, --help            show this help message and exit
  --url_file URL_FILE   URL list (default: url.txt)
  --discord_webhook_url DISCORD_WEBHOOK_URL
                        Discord webhook URL (default: None)
  --sample              Use sample URL list (default: False)
  --clear               Clear archive directory (default: False)
```
