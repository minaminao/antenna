# antenna
サイトを巡回して更新があったらDiscordに教えてくれる君。

## Usage

```
$ crontab -e
```

```
* * * * * <Pythonの絶対パス> <antenna.pyの絶対パス> --discord_webhook_url <Discord Webhook URL>
```