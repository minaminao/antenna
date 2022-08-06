# antenna
サイトを巡回して更新があったらDiscordに教えてくれる君。

## Usage

url.jsonに以下のように記述。
```json
[
    {
        "type": "text",
        "url":"http://worldclockapi.com/api/json/utc/now"
    },
    {
        "type": "text",
        "url":"http://worldclockapi.com/api/json/est/now",
        "pattern": "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}"
    },
    {
        "type": "rss",
        "url": "http://feeds.feedburner.com/oreilly/newbooks",
        "title": "O'Reilly New Books"
    }
]
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
$ python antenna.py --sample
UPDATED: http://worldclockapi.com/api/json/utc/now
--- Previous
+++ Current
@@ -1 +1 @@
-{"$id":"1","currentDateTime":"2021-11-23T08:40Z", ... 6,"ordinalDate":"2021-327","serviceResponse":null}
+{"$id":"1","currentDateTime":"2021-11-28T16:05Z", ... 0,"ordinalDate":"2021-332","serviceResponse":null}

UPDATED: http://worldclockapi.com/api/json/est/now
--- Previous
+++ Current
@@ -1 +1 @@
-2021-11-28T11:20
+2021-11-28T11:21
```

## Options

```
usage: antenna.py [-h] [--url_file URL_FILE] [--discord] [--discord_webhook_url DISCORD_WEBHOOK_URL] [--sample] [--clear] [--line_length_limit LINE_LENGTH_LIMIT]
                  [--number_of_context_lines NUMBER_OF_CONTEXT_LINES] [--no_archive] [--show]

options:
  -h, --help            show this help message and exit
  --url_file URL_FILE   URL list (default: url.txt)
  --discord             Notify Discord using local webhook url file (default: False)
  --discord_webhook_url DISCORD_WEBHOOK_URL
                        Discord webhook URL (default: None)
  --sample              Use sample URL list (default: False)
  --clear               Clear archive directory (default: False)
  --line_length_limit LINE_LENGTH_LIMIT
                        Line length limit of diff (default: 100)
  --number_of_context_lines NUMBER_OF_CONTEXT_LINES
                        Number of context lines (default: 1)
  --no_archive          Do not archive sites (default: False)
  --show                Show content (default: False)
```
