# antenna
サイトを巡回して更新があったらDiscordに教えてくれる君。

## Usage

url.txtに以下のように記述。
```
https://foo/
https://bar/
```

cronを設定。

```
$ crontab -e
```
```
* * * * * <Pythonの絶対パス> <antenna.pyの絶対パス> --discord_webhook_url <Discord webhook URL>
```

## Sample Output
```
UPDATED: http://worldclockapi.com/api/json/utc/now
--- old
+++ new
@@ -1 +1 @@
-{"$id":"1","currentDateTime":"2021-11-23T06:16Z","utcOffset":"00:00:00","isDayLightSavingsTime":false,"dayOfTheWeek":"Tuesday","timeZoneName":"UTC","currentFileTime":132821217816515389,"ordinalDate":"2021-327","serviceResponse":null}
+{"$id":"1","currentDateTime":"2021-11-23T06:16Z","utcOffset":"00:00:00","isDayLightSavingsTime":false,"dayOfTheWeek":"Tuesday","timeZoneName":"UTC","currentFileTime":132821217907770782,"ordinalDate":"2021-327","serviceResponse":null}
```

## Options

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
